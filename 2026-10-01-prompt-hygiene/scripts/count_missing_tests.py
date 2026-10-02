#!/usr/bin/env python3
"""數各輪「缺測試」類 finding（跑前預期：A、B 都是 0）。命中的逐筆印出，人工確認不是誤中。

用法：python3 scripts/count_missing_tests.py ph-A1 ph-B1 ph-A2 ph-B2 [v00 ...]
"""

import json
import pathlib
import re
import sys

ROUNDS = pathlib.Path(__file__).resolve().parents[2] / "2026-09-24-confidence-loop" / "rounds"
PAT = re.compile(
    r"沒有(?:對應的?)?(?:單元)?測試|缺(?:少)?(?:單元)?測試|未(?:經)?測試|測試覆蓋|沒有被測到|補(?:上)?(?:單元)?測試"
    r"|missing (?:unit )?tests?|no (?:unit )?tests?\b|untested|test coverage",
    re.I,
)
FIELDS = ("title", "body", "evidence", "suggestion")


def main() -> int:
    for label in sys.argv[1:]:
        rdir = ROUNDS / label
        n_find = n_hit = 0
        hits = []
        for path in sorted(rdir.glob("*-*.json")):
            try:
                items = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if not isinstance(items, list):
                continue
            for f in items:
                n_find += 1
                text = " ".join(str(f.get(k, "")) for k in FIELDS)
                m = PAT.search(text)
                if m:
                    n_hit += 1
                    hits.append(f"{path.stem}: [{m.group(0)}] {str(f.get('title', ''))[:80]}")
        print(f"{label}: finding {n_find}、缺測試 {n_hit}")
        for h in hits:
            print(f"    - {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
