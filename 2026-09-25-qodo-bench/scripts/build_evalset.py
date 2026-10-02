#!/usr/bin/env python3
"""從 Qodo GT 建評估集：每則 issue 在 diff 新檔側的錨點範圍。

錨點的決定順序（片段優先，理由同 locate.py：GT 的 start_line 538 則裡只有 285 則剛好對上）：
  1. snippet  片段各行（去空白後 ≥ 8 字元）比對新檔側的 + 行與 context 行，取吻合行數最多的那一段
  2. removal  片段只出現在刪除行 → 錨點是刪除發生處在新檔側的位置
  3. line     片段找不到、但檔案在 diff 裡且有 start_line → 用 GT 自己的行號範圍
  4. 都沒有   reachable=false（只看 diff 的架構看不到它）

輸出 evalset.json。只讀本地檔案，$0。
"""
import collections
import json
import pathlib
import re
import sys

EXP = pathlib.Path(__file__).resolve().parents[1]
KIT = EXP.parents[2]
sys.path.insert(0, str(KIT / ".github/scripts"))
import locate  # noqa: E402

HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
GIT = re.compile(r"^diff --git a/(.+?) b/(.+)$")
MIN = locate.MIN_SNIPPET_LEN


def parse(diff: str) -> dict:
    """{path: {"new": {n: text}, "kind": {n: '+'|' '}, "removed": [(old_text, new_pos)]}}"""
    files, cur, o, n = {}, None, 0, 0
    for raw in diff.splitlines():
        m = GIT.match(raw)
        if m:
            cur = files.setdefault(m.group(2), {"new": {}, "kind": {}, "removed": []})
            continue
        if cur is None or raw.startswith(("+++ ", "--- ")):
            continue
        h = HUNK.match(raw)
        if h:
            o, n = int(h.group(1)), int(h.group(2))
            continue
        if raw.startswith("+"):
            cur["new"][n], cur["kind"][n] = raw[1:], "+"
            n += 1
        elif raw.startswith("-"):
            cur["removed"].append((raw[1:], n))
            o += 1
        elif raw.startswith(" "):
            cur["new"][n], cur["kind"][n] = raw[1:], " "
            o += 1
            n += 1
    return files


def snippet_lines(snippet: str) -> list[str]:
    out = []
    for ln in (snippet or "").splitlines():
        s = locate.normalize_ws(ln)
        if len(s) >= MIN and s not in out:
            out.append(s)
    return out


def best_window(hits: dict[str, list[int]], span: int) -> list[int]:
    """hits: 片段行 → 吻合的新檔行號。找一個長度 span 的視窗，涵蓋最多「不同的片段行」。"""
    points = sorted({(ln, s) for s, lns in hits.items() for ln in lns})
    best, best_cov = [], 0
    for i, (start, _) in enumerate(points):
        inside = [(ln, s) for ln, s in points[i:] if ln <= start + span]
        cov = len({s for _, s in inside})
        if cov > best_cov:
            best_cov, best = cov, [ln for ln, _ in inside]
    return best


def anchor(issue: dict, files: dict) -> dict:
    lines = snippet_lines(issue.get("problematic_code_snippet", ""))
    path = issue.get("file_path")
    cands = {path: files[path]} if path in files else ({} if path else files)
    span = max(len(lines), 1) + 6

    # 1) 新檔側（+ 與 context）
    per_file = {}
    for p, f in cands.items():
        hits = collections.defaultdict(list)
        for s in lines:
            for ln, text in f["new"].items():
                if s in locate.normalize_ws(text):
                    hits[s].append(ln)
        if hits:
            win = best_window(hits, span)
            per_file[p] = (len({s for s in hits if any(ln in win for ln in hits[s])}), win)
    if per_file:
        # 沒給 file_path 時，只接受唯一一個檔案有吻合（同 locate.py 跨檔規則）
        if not path and len(per_file) > 1:
            return {"reachable": False, "how": "片段跨多個檔案吻合"}
        p, (cov, win) = max(per_file.items(), key=lambda kv: kv[1][0])
        kinds = {files[p]["kind"][ln] for ln in win}
        return {"reachable": True, "how": "snippet", "file": p, "lo": min(win), "hi": max(win),
                "anchor_kind": "+" if kinds == {"+"} else "ctx" if kinds == {" "} else "mixed",
                "coverage": f"{cov}/{len(lines)}"}

    # 2) 只在刪除行
    for p, f in cands.items():
        pos = [np for text, np in f["removed"] if any(s in locate.normalize_ws(text) for s in lines)]
        if pos:
            return {"reachable": True, "how": "removal", "file": p, "lo": min(pos), "hi": max(pos),
                    "anchor_kind": "removed"}

    # 3) GT 自己的行號
    if path in files and isinstance(issue.get("start_line"), int):
        lo = issue["start_line"]
        hi = issue["end_line"] if isinstance(issue.get("end_line"), int) else lo
        return {"reachable": True, "how": "line", "file": path, "lo": lo, "hi": max(lo, hi),
                "anchor_kind": "line"}

    if path and path not in files:
        return {"reachable": False, "how": "檔案不在 diff"}
    return {"reachable": False, "how": "片段找不到且沒有可用行號"}


def main() -> None:
    rows = [json.loads(l) for l in (EXP / "data/bench.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    evalset = []
    for r in rows:
        parts = r["pr_url_to_review"].rstrip("/").split("/")
        key = f"{parts[-3]}-{parts[-1]}"
        files = parse((EXP / "prs" / key / "pr.diff").read_text(encoding="utf-8"))
        for i, g in enumerate(r["issues"]):
            a = anchor(g, files)
            evalset.append({"id": f"{key}#{i}", "pr": key, "repo": r["repo"],
                            "kind": "rule" if (g.get("rule_name") or "").strip() else "func",
                            "title": g.get("title"), "description": g.get("description"),
                            "gt_file": g.get("file_path"), "gt_start": g.get("start_line"),
                            "snippet": g.get("problematic_code_snippet"), **a})
    (EXP / "evalset.json").write_text(json.dumps(evalset, ensure_ascii=False, indent=1), encoding="utf-8")

    c = collections.Counter((e["kind"], e["how"], e.get("anchor_kind", "-")) for e in evalset)
    for k, v in sorted(c.items()):
        print(f"{k[0]:<5} {k[1]:<22} {k[2]:<8} {v}")
    for kind in ("func", "rule"):
        sub = [e for e in evalset if e["kind"] == kind]
        print(f"{kind}: {len(sub)} 則，diff 內可定錨 {sum(e['reachable'] for e in sub)}")


if __name__ == "__main__":
    main()
