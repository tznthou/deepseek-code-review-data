#!/usr/bin/env python3
"""組「函式上下文」那一臂的 diff（prs/<key>/fc.diff）。$0。

每個檔案區塊（`diff --git` 到下一個 `diff --git`）：
  程式碼檔（副檔名在 CODE_EXT）→ 用 wd.diff 的區塊（`git diff -W`，內建 driver 版）
  其他（JSON／YAML／lock／markdown／無副檔名…）→ 逐字沿用 Qodo 的 pr.diff 區塊
理由：沒有函式結構的檔案，git 找不到「函式開頭」，-W 會把整個檔案塞進來
（tauri-1 的兩個 config.schema.json 各放大約 100 倍；2026-09-30 實測）。

不變量（任一條不成立就停）：
  1. 檔案區塊的順序與標頭行（diff --git）與 Qodo 相同
  2. 每個檔案的 +／- 行序列與 Qodo 相同——只有上下文不同
  3. 非程式碼檔的區塊與 Qodo 逐字相同（由組法保證，這裡再驗一次）

超過 LIMIT 字元的 PR 整份退回 Qodo 的 pr.diff（跑前寫定，見 README「操作定義」），manifest 記 fallback。
輸出 prs/fc-manifest.json（每個 PR 的大小、倍率、fallback、程式碼檔數）。

用法：compose_fc.py
"""
import json
import pathlib
import sys

EXP = pathlib.Path(__file__).resolve().parents[1]
QODO = EXP.parent / "2026-09-25-qodo-bench"
LIMIT = 400_000  # deepseek_review.py 的 DEFAULT_MAX_DIFF_CHARS
CODE_EXT = {".swift", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".py", ".pyi", ".rs", ".cs", ".razor",
            ".c", ".h", ".cc", ".cpp", ".hpp", ".go", ".java", ".kt", ".kts", ".rb", ".php", ".m", ".sh",
            ".ps1", ".tcl"}


def blocks(diff: str) -> list[tuple[str, str]]:
    """[(diff --git 那一行, 整個區塊文字)]。區塊文字含結尾換行，串回去等於原文。"""
    out, cur = [], []
    for line in diff.splitlines(keepends=True):
        if line.startswith("diff --git ") and cur:
            out.append((cur[0].rstrip("\n"), "".join(cur)))
            cur = []
        cur.append(line)
    if cur:
        out.append((cur[0].rstrip("\n"), "".join(cur)))
    return out


def changes(block: str) -> list[str]:
    """區塊裡的 +／- 行（跳過 --- ／+++ 標頭）。"""
    out, in_hunk = [], False
    for line in block.splitlines():
        if line.startswith("@@"):
            in_hunk = True
            continue
        if in_hunk and line[:1] in "+-":
            out.append(line)
    return out


def path_of(header: str) -> str:
    return header.split(" b/", 1)[-1]


def main() -> None:
    rows, bad = [], []
    for d in sorted(p for p in (EXP / "prs").iterdir() if (p / "wd.diff").exists()):
        qodo = (QODO / "prs" / d.name / "pr.diff").read_text(encoding="utf-8")
        wd = (d / "wd.diff").read_text(encoding="utf-8")
        qb, wb = blocks(qodo), blocks(wd)
        if [h for h, _ in qb] != [h for h, _ in wb]:
            bad.append(f"{d.name}: 檔案區塊順序或標頭不同")
            continue
        parts, n_code, n_other = [], 0, 0
        for (h, q), (_, w) in zip(qb, wb):
            if changes(q) != changes(w):
                bad.append(f"{d.name}: {path_of(h)} 的 +／- 行序列不同")
            if pathlib.PurePath(path_of(h)).suffix.lower() in CODE_EXT:
                parts.append(w)
                n_code += 1
            else:
                parts.append(q)
                n_other += 1
        fc = "".join(parts)
        for (h, q), (_, f) in zip(qb, blocks(fc)):
            if pathlib.PurePath(path_of(h)).suffix.lower() not in CODE_EXT and q != f:
                bad.append(f"{d.name}: 非程式碼檔 {path_of(h)} 沒有逐字沿用")
        fallback = len(fc) > LIMIT
        (d / "fc.diff").write_text(qodo if fallback else fc, encoding="utf-8")
        rows.append({"key": d.name, "qodo": len(qodo), "fc_composed": len(fc), "fallback": fallback,
                     "sent": len(qodo) if fallback else len(fc),
                     "ratio": round((len(qodo) if fallback else len(fc)) / len(qodo), 2),
                     "code_files": n_code, "other_files": n_other})
    (EXP / "prs" / "fc-manifest.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    tot_q = sum(r["qodo"] for r in rows)
    tot_s = sum(r["sent"] for r in rows)
    print(f"PR {len(rows)}｜不變量違反 {len(bad)}｜fallback {sum(r['fallback'] for r in rows)} "
          f"{[r['key'] for r in rows if r['fallback']]}")
    print(f"總字元：Qodo {tot_q:,} → fc {tot_s:,}（×{tot_s / tot_q:.2f}）")
    for b in bad[:20]:
        print("  ✗", b)
    sys.exit(1 if bad or len(rows) != 100 else 0)


if __name__ == "__main__":
    main()
