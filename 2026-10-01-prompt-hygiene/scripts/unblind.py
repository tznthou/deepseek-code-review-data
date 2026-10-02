#!/usr/bin/env python3
"""blind-labels.csv（匿名編號）→ 各輪的 labels-manual.csv（原 id）。

每一筆人工判定都必須有標記；抽查只寫有異議的。label 只能是 valid／invalid／disputed。
用法：python3 scripts/unblind.py
"""

import csv
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
LOOP = HERE.parent / "2026-09-24-confidence-loop"
# 第二批：python3 scripts/unblind.py --dir blind2
BLIND = HERE / (sys.argv[2] if sys.argv[1:2] == ["--dir"] else "blind")
OK = {"valid", "invalid", "disputed"}


def main() -> int:
    mapping = json.loads((BLIND / "blind-map.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((BLIND / "blind-labels.csv").open(encoding="utf-8")))
    seen = {r["code"] for r in rows}
    missing = sorted(c for c in mapping if c.startswith("M") and c not in seen)
    bad = [r for r in rows if r["label"] not in OK or r["code"] not in mapping]
    dup = len(rows) - len(seen)
    if missing or bad or dup:
        sys.exit(f"[停] 人工判定缺 {len(missing)} 筆 {missing[:5]}；不合法 {len(bad)} 筆；重複 {dup} 筆")

    per_round: dict[str, list[dict]] = {}
    for r in rows:
        fid = mapping[r["code"]]
        per_round.setdefault(fid.split(":", 1)[0], []).append(
            {"id": fid, "item": r["item"], "label": r["label"], "reason": r["reason"]})
    for lab, items in sorted(per_round.items()):
        with (LOOP / "rounds" / lab / "labels-manual.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["id", "item", "label", "reason"])
            w.writeheader()
            w.writerows(items)
        print(f"{lab}: labels-manual.csv {len(items)} 筆")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
