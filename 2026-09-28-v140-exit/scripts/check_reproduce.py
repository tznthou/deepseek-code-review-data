#!/usr/bin/env python3
"""計分邏輯的正向對照：用 score_exit 同一套算法，重現 09-25 Qodo README 的公開數字才信它。
預期：功能性位置命中 base-1 0.573、base-2 0.576；base-1 同一問題（09-25 舊標籤）0.443。"""
import csv
import json
import pathlib
import sys

sys.dont_write_bytecode = True
EXIT = pathlib.Path(__file__).resolve().parents[1]
QODO = EXIT.parent / "2026-09-25-qodo-bench"
sys.path.insert(0, str(QODO / "scripts"))
import score_bench  # noqa: E402

evalset = json.loads((QODO / "evalset.json").read_text(encoding="utf-8"))
func = {e["id"] for e in evalset if e["kind"] == "func"}
with open(QODO / "rounds/base-1/labels.csv", newline="", encoding="utf-8") as fh:
    old = {r["pair"].strip(): r["label"].strip().lower() for r in csv.DictReader(fh)}

for r, want_loc in (("base-1", 0.573), ("base-2", 0.576)):
    _, by_pr, findings = score_bench.load_round(r)
    pairs = score_bench.pairs_for(findings, by_pr)
    loc = {p["gid"] for p in pairs if p["loc_hit"] and p["gid"] in func}
    line = f"{r}：位置命中 {len(loc)}/{len(func)} = {len(loc) / len(func):.3f}（預期 {want_loc}）"
    if r == "base-1":
        saved = json.loads((QODO / "rounds/base-1/pairs.json").read_text(encoding="utf-8"))
        same = {p["gid"] for p in pairs if p["gid"] in func and old.get(p["pair"]) == "same"}
        line += (f"｜同一問題 {len(same)}/{len(func)} = {len(same) / len(func):.3f}（預期 0.443）"
                 f"｜重算配對 {len(pairs)} vs 09-25 存檔 {len(saved)}，編號一致 "
                 f"{len({p['pair'] for p in pairs} & {p['pair'] for p in saved})}")
    print(line)
