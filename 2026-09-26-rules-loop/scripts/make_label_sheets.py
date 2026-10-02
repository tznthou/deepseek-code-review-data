#!/usr/bin/env python3
"""holdout 盲標：v00（base-1、base-2）與 v01（hold-v01a、hold-v01b）的候選配對混在一起、打亂、拆成幾份標記單。

盲的程度：
- 配對編號是不透明的 P0001…，對照表寫在 blind/mapping.json（標記員不准讀）
- finding 裡的規則編號（[R06]、（R03）…）拿掉，不然一眼看出是注入規範的那組
- 不給 confidence、severity（同 Qodo 那次）
判準與 Qodo 盲標相同（Martian）：一個 code change 能同時修掉兩者才算 same。

另外分層抽 30 組給主 session 先標（位置命中 20、其他 10），在看標記員結果之前完成。
用法：make_label_sheets.py [份數=5]
"""
import collections
import json
import random
import re
import sys

sys.dont_write_bytecode = True
from common import LOOP, QODO, split_prs  # noqa: E402
import loop_score as ls  # noqa: E402
import score_bench  # noqa: E402

RUNS = {"base-1": "v00", "base-2": "v00", "hold-v01a": "v01", "hold-v01b": "v01"}
SEED = 20260926
OUT = LOOP / "blind"
ID_RE = re.compile(r"\s*[\[(（【]\s*R\d{2}\s*[\])）】]\s*|\bR\d{2}\b")

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


def strip_ids(s: str) -> str:
    return ID_RE.sub(" ", s or "").strip()


def block(pid: str, e: dict, f: dict, p: dict) -> str:
    snip = [l.strip() for l in (e["snippet"] or "").splitlines() if l.strip()][:4]
    fsnip = [l.strip() for l in (f["existing_code"] or "").splitlines()][:4]
    return "\n".join([
        f"## {pid}", "",
        f"**GT**（{e['kind']}）{e['title']}", "", f"> {e['description']}", "",
        "GT 片段：`" + " ⏎ ".join(snip)[:300] + "`", "",
        f"**finding**（`{f['path']}:{f['line'] or f['model_line']}`，距錨點 {p['dist']} 行）{strip_ids(f['title'])}", "",
        f"> {strip_ids(f['body'])[:900]}", "",
        "finding 片段：`" + " ⏎ ".join(fsnip)[:300] + "`", ""])


def main() -> None:
    parts = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    if OUT.exists():
        sys.exit(f"[stop] {OUT} 已存在，不覆寫（標記單產生一次就定了）")
    prs = split_prs("holdout")
    evalset = [e for e in json.loads((QODO / "evalset.json").read_text(encoding="utf-8")) if e["pr"] in set(prs)]
    emap = {e["id"]: e for e in evalset}
    by_pr = collections.defaultdict(list)
    for e in evalset:
        by_pr[e["pr"]].append(e)

    items = []
    for label in RUNS:
        findings, missing = ls.load_findings(label, prs)
        assert not missing, f"{label} 缺 {missing}"
        fmap = {f["fid"]: f for f in findings}
        for p in score_bench.pairs_for(findings, by_pr):
            items.append((label, p, fmap[p["fid"]], emap[p["gid"]]))

    rng = random.Random(SEED)
    rng.shuffle(items)
    OUT.mkdir()
    mapping, blocks = {}, []
    for i, (label, p, f, e) in enumerate(items, 1):
        pid = f"P{i:04d}"
        mapping[pid] = {"run": label, "cond": RUNS[label], "fid": p["fid"], "gid": p["gid"], "kind": e["kind"],
                        "via": p["via"], "dist": p["dist"], "loc_hit": p["loc_hit"],
                        "qodo_pair": p["pair"] if label == "base-1" else None}
        blocks.append((pid, block(pid, e, f, p)))
    (OUT / "mapping.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")

    size = -(-len(blocks) // parts)
    for k in range(parts):
        chunk = blocks[k * size:(k + 1) * size]
        csv_path = OUT / f"labels-part{k + 1}.csv"
        text = HEADER.format(part=k + 1, csv=csv_path) + "\n".join(b for _, b in chunk)
        (OUT / f"sheet-part{k + 1}.md").write_text(text, encoding="utf-8")
        print(f"sheet-part{k + 1}.md：{len(chunk)} 組")

    # 主 session 的抽樣：位置命中 20、其他 10，兩個條件大致各半
    loc = [pid for pid, m in mapping.items() if m["loc_hit"]]
    other = [pid for pid, m in mapping.items() if not m["loc_hit"]]
    spot = sorted(random.Random(SEED + 1).sample(loc, 20) + random.Random(SEED + 2).sample(other, 10))
    bmap = dict(blocks)
    (OUT / "spot-sheet.md").write_text(HEADER.format(part="（主 session 抽樣）", csv=OUT / "spot-main.csv")
                                       + "\n".join(bmap[p] for p in spot), encoding="utf-8")
    c = collections.Counter((m["cond"], m["kind"]) for m in mapping.values())
    print(f"共 {len(blocks)} 組：{dict(c)}｜主 session 抽樣 30 組（位置命中 20、其他 10）")


if __name__ == "__main__":
    main()
