#!/usr/bin/env python3
"""v1.4.0 出口的盲標：v131-1 的全部候選配對＋base-1 裡 finding 信心 ≥ 0.6 的候選配對，混在一起、打亂、拆成幾份標記單。

盲的程度（照 rules loop 的 make_label_sheets.py）：
- 配對編號是不透明的 P0001…，對照表寫在 blind/mapping.json（標記員不准讀）
- 標記單不含 confidence、severity、輪次
判準（Martian）與 09-25 Qodo、09-26 rules loop 相同：一個 code change 能同時修掉兩者才算 same。
另外分層抽 30 組給主 session 先標（位置命中 20、其他 10），在讀標記員結果之前完成。

用法：make_sheets.py [每份組數=100]
"""
import collections
import json
import pathlib
import random
import sys

sys.dont_write_bytecode = True
EXIT = pathlib.Path(__file__).resolve().parents[1]
QODO = EXIT.parent / "2026-09-25-qodo-bench"
sys.path.insert(0, str(QODO / "scripts"))
import score_bench  # noqa: E402（它會再 import kit 的 locate.py，與 09-25 同一份 code）

SEED = 20260928
OUT = EXIT / "blind"
RUNS = {"v131-1": 0.0, "base-1": 0.6}  # 輪次 → 收進標記單的信心下限（README「操作定義」）

HEADER = """# 盲標單 {part}：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`{csv}`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
"""


def block(pid: str, e: dict, f: dict, p: dict) -> str:
    snip = [l.strip() for l in (e["snippet"] or "").splitlines() if l.strip()][:4]
    fsnip = [l.strip() for l in (f["existing_code"] or "").splitlines()][:4]
    return "\n".join([
        f"## {pid}", "",
        f"**GT**（{e['kind']}）{e['title']}", "", f"> {e['description']}", "",
        "GT 片段：`" + " ⏎ ".join(snip)[:300] + "`", "",
        f"**finding**（`{f['path']}:{f['line'] or f['model_line']}`，距錨點 {p['dist']} 行）{f['title']}", "",
        f"> {(f['body'] or '')[:900]}", "",
        "finding 片段：`" + " ⏎ ".join(fsnip)[:300] + "`", ""])


def main() -> None:
    per_part = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    if OUT.exists():
        sys.exit(f"[stop] {OUT} 已存在，不覆寫（標記單產生一次就定了）")

    items = []
    for label, floor in RUNS.items():
        man = json.loads((QODO / "rounds" / label / "manifest.json").read_text(encoding="utf-8"))
        ok = sum(r.get("exit") == 0 for r in man["results"].values())
        if ok != 100:
            sys.exit(f"[stop] {label} 只有 {ok}/100 個 PR 成功，先補跑")
        evalset, by_pr, findings = score_bench.load_round(label)
        fmap = {f["fid"]: f for f in findings}
        emap = {e["id"]: e for e in evalset}
        for p in score_bench.pairs_for(findings, by_pr):
            f = fmap[p["fid"]]
            if f["confidence"] >= floor:
                items.append((label, p, f, emap[p["gid"]]))

    rng = random.Random(SEED)
    rng.shuffle(items)
    OUT.mkdir()
    mapping, blocks = {}, []
    for i, (label, p, f, e) in enumerate(items, 1):
        pid = f"P{i:04d}"
        mapping[pid] = {"run": label, "fid": p["fid"], "gid": p["gid"], "kind": e["kind"], "via": p["via"],
                        "dist": p["dist"], "loc_hit": p["loc_hit"], "conf": f["confidence"],
                        "severity": f["severity"], "qodo_pair": p["pair"] if label == "base-1" else None}
        blocks.append((pid, block(pid, e, f, p)))
    (OUT / "mapping.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")

    parts = -(-len(blocks) // per_part)
    size = -(-len(blocks) // parts)
    for k in range(parts):
        chunk = blocks[k * size:(k + 1) * size]
        csv_path = OUT / f"labels-part{k + 1}.csv"
        text = HEADER.format(part=k + 1, csv=csv_path) + "\n".join(b for _, b in chunk)
        (OUT / f"sheet-part{k + 1}.md").write_text(text, encoding="utf-8")
        print(f"sheet-part{k + 1}.md：{len(chunk)} 組")

    loc = [pid for pid, m in mapping.items() if m["loc_hit"]]
    other = [pid for pid, m in mapping.items() if not m["loc_hit"]]
    spot = sorted(random.Random(SEED + 1).sample(loc, 20) + random.Random(SEED + 2).sample(other, 10))
    bmap = dict(blocks)
    (OUT / "spot-sheet.md").write_text(HEADER.format(part="（主 session 抽樣）", csv=OUT / "spot-main.csv")
                                       + "\n".join(bmap[p] for p in spot), encoding="utf-8")
    c = collections.Counter((m["run"], m["kind"]) for m in mapping.values())
    print(f"共 {len(blocks)} 組：{dict(c)}｜主 session 抽樣 30 組（位置命中 20、其他 10）")


if __name__ == "__main__":
    main()
