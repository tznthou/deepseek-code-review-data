#!/usr/bin/env python3
"""只驗一份標記結果的格式（不對回輪次、不算任何指標）：編號與標記單一致、標籤合法、沒有重複。
用法：check_part.py <份號>…"""
import csv
import pathlib
import re
import sys

B = pathlib.Path(__file__).resolve().parents[1] / "blind"
for k in sys.argv[1:]:
    sheet_ids = re.findall(r"^## (P\d{4})$", (B / f"sheet-part{k}.md").read_text(encoding="utf-8"), re.M)
    path = B / f"labels-part{k}.csv"
    if not path.exists():
        print(f"part{k}：還沒有 CSV")
        continue
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ids = [r["pair"].strip() for r in rows]
    labs = [r["label"].strip().lower() for r in rows]
    bad = [(i, l) for i, l in zip(ids, labs) if l not in ("same", "partial", "no")]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    miss = sorted(set(sheet_ids) - set(ids))
    extra = sorted(set(ids) - set(sheet_ids))
    ok = not (bad or dup or miss or extra)
    print(f"part{k}：標記單 {len(sheet_ids)} 組｜CSV {len(rows)} 行｜不合法 {len(bad)}｜重複 {len(dup)}｜缺 {len(miss)}｜多 {len(extra)}"
          f" → {'OK' if ok else '有問題'}" + ("" if ok else f"  {bad[:3]} {dup[:3]} {miss[:5]} {extra[:5]}"))
