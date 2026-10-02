#!/usr/bin/env python3
"""從 stdin 讀「code|item|label|reason」一行一筆，用 csv 模組附加到 blind/blind-labels.csv。

同一個 code 重複出現就停（避免標兩次）；label 只收 valid／invalid／disputed。
"""

import csv
import pathlib
import sys

# 第二批：python3 scripts/append_labels.py --dir blind2 <<'ROWS' …
_DIR = sys.argv[2] if sys.argv[1:2] == ["--dir"] else "blind"
OUT = pathlib.Path(__file__).resolve().parent.parent / _DIR / "blind-labels.csv"
OK = {"valid", "invalid", "disputed"}

existing = {r["code"] for r in csv.DictReader(OUT.open(encoding="utf-8"))}
rows = []
for raw in sys.stdin.read().splitlines():
    if not raw.strip():
        continue
    code, item, label, reason = (x.strip() for x in raw.split("|", 3))
    if label not in OK:
        sys.exit(f"[停] {code} 的 label 不合法：{label}")
    if code in existing or code in {r[0] for r in rows}:
        sys.exit(f"[停] {code} 已經標過")
    rows.append((code, item, label, reason))
with OUT.open("a", encoding="utf-8", newline="") as fh:
    csv.writer(fh).writerows(rows)
print(f"附加 {len(rows)} 筆，累計 {len(existing) + len(rows)} 筆")
