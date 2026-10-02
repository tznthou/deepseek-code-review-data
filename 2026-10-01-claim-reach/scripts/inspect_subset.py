#!/usr/bin/env python3
"""檢查 AACR 子集的筆數（陽性對照）與 note 的語言分布，只印 note、不印 label。

用法：python3 scripts/inspect_subset.py
"""

import json
import pathlib
import random
import re

HERE = pathlib.Path(__file__).resolve().parent.parent
DATA = HERE / "data" / "dataset.json"

rows = json.loads(DATA.read_text(encoding="utf-8"))
print(f"全體 {len(rows)} 筆")

subset = [r for r in rows if r.get("is_ai_comment") is True and r.get("context") == "Diff Level"]
pos = sum(1 for r in subset if r.get("label") == 1)
neg = sum(1 for r in subset if r.get("label") == 0)
print(f"子集（AI ∧ Diff Level）{len(subset)} 筆 = 正確 {pos} / 錯誤 {neg}")
print("  陽性對照：memory 記載 760 = 558 / 202")

cjk = re.compile(r"[一-鿿]")
n_cjk = sum(1 for r in subset if cjk.search(r.get("note") or ""))
print(f"note 含中文字的筆數：{n_cjk} / {len(subset)}")

random.seed(20261001)
print("\n--- 隨機 8 則 note（只看語言與句型，不看 label）---")
for r in random.sample(subset, 8):
    note = (r.get("note") or "").replace("\n", " ")
    print(f"- [{r.get('category')}] {note[:220]}")
