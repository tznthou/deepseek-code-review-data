#!/usr/bin/env python3
"""classify 的已知答案測試：用 #50／#51 的真實數字當輸入，答案照 README 的判定規則手算。"""
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("cp", pathlib.Path(__file__).with_name("cache_probe.py"))
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)


def row(size, structure, p1, c1, c2):
    return {"size": size, "structure": structure, "call1": {"prompt_tokens": p1, "cached": c1},
            "call2": {"cached": c2}}


rows = cp.classify([
    row("S", "c", 2469, 1536, 2432),  # #51：floor64(2469)=2432 → full
    row("S", "d", 4000, 1536, 1536),  # P=2469（S-c 平均）；1536 ≤ 1536+64 → baseline
    row("S", "d", 4000, 1536, 2000),  # 介於中間 → partial
    row("L", "c", 6400, 1536, 6336),  # floor64(6400)−64=6336 → full（剛好等於門檻）
    row("L", "d", 8000, 1536, 1600),  # P=6400；1600 ≤ 1600 → baseline（剛好等於門檻）
    row("L", "d", 8000, 0, 65),       # 第一次 cached=0；65 > 64 且遠小於 P → partial
])
want = ["full", "baseline", "partial", "full", "baseline", "partial"]
got = [r["class"] for r in rows]
for r, w in zip(rows, want):
    print(("PASS " if r["class"] == w else "FAIL ") + f"{r['size']}-{r['structure']} P={r['P']} → {r['class']}（要 {w}）")
print("ALL PASS" if got == want else "有 FAIL")
