#!/usr/bin/env python3
"""verdict 主數字的獨立重算：不 import score_ctx，只讀 blind/mapping.json、labels-part*.csv 與各輪 manifest。$0。

目的：verdict 只有一條計算路徑，數字錯了看不出來。這裡用另一種寫法（直接從 mapping 的欄位聚合）重算
S（功能性／規則類）、P、R，跟 verdict 印出的數字逐項比對。
L 需要 locate，不在這裡重算——它已被 `score_ctx.py check` 的正向對照（重現 base-1／2 的 177／178）驗過。
"""
import collections
import csv
import json
import pathlib
import sys

EXP = pathlib.Path(__file__).resolve().parents[1]
BLIND = EXP / "blind"
ROUND_DIR = {"base-3": EXP / "arms/base/rounds/base-3", "fc-1": EXP / "arms/fc/rounds/fc-1"}
# verdict 印出的數字（S 功能性、S 規則類、P 分子、R 分子）；不一致就紅
EXPECT = {"fc-1": (134, 23, 155, 157), "base-3": (130, 37, 162, 167)}
N_ALL = 580

mapping = json.loads((BLIND / "mapping.json").read_text(encoding="utf-8"))
labels: dict[str, str] = {}
for part in sorted(BLIND.glob("labels-part*.csv")):
    with open(part, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            labels[row["pair"].strip()] = row["label"].strip().lower()
assert set(labels) == set(mapping), (len(labels), len(mapping))

ok = True
for run in ("fc-1", "base-3"):
    man = json.loads((ROUND_DIR[run] / "manifest.json").read_text(encoding="utf-8"))["results"]
    n_find = sum(v["findings"] or 0 for v in man.values())
    rows = [(pid, m) for pid, m in mapping.items() if m["run"] == run]
    same = [m for pid, m in rows if labels[pid] == "same"]
    s_func = len({m["gid"] for m in same if m["kind"] == "func"})
    s_rule = len({m["gid"] for m in same if m["kind"] == "rule"})
    f_ok = len({m["fid"] for m in same})
    g_ok = len({m["gid"] for m in same})
    dist = collections.Counter(labels[pid] for pid, _ in rows)
    got = (s_func, s_rule, f_ok, g_ok)
    ok &= got == EXPECT[run]
    print(f"{run}：配對 {len(rows)}（{dict(dist)}）｜finding {n_find}")
    print(f"  獨立重算 S 功能性 {s_func}／規則類 {s_rule}｜P {f_ok}/{n_find} = {f_ok / n_find:.3f}｜R {g_ok}/{N_ALL} = {g_ok / N_ALL:.3f}"
          f"｜F1 {2 * (f_ok / n_find) * (g_ok / N_ALL) / ((f_ok / n_find) + (g_ok / N_ALL)):.3f}")
    print(f"  verdict 印出   S 功能性 {EXPECT[run][0]}／規則類 {EXPECT[run][1]}｜P 分子 {EXPECT[run][2]}｜R 分子 {EXPECT[run][3]}"
          f" → {'一致' if got == EXPECT[run] else '✗ 不一致'}")
print("全部一致" if ok else "✗ 有數字對不上，先查 score_ctx.py 的 verdict")
sys.exit(0 if ok else 1)
