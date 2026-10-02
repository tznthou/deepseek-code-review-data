#!/usr/bin/env python3
"""③ claim 型 grep 反駁的射程：AACR 子集上「斷言不存在」句型的 label 組成。

規則在跑前寫死（見 README「跑前定稿」）。輸出：
  - 四格（label × 是否在射程內），absence 與 broad 兩種定義各一份
  - precision 上限：射程內錯的全部刪掉、對的一筆不誤刪
  - out/reach.csv：逐筆結果，供抽查

用法：python3 scripts/reach.py [--audit N]
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import random
import re

HERE = pathlib.Path(__file__).resolve().parent.parent
DATA = HERE / "data" / "dataset.json"
OUT = HERE / "out"

# ③ 本體：斷言某個東西不存在／沒做。grep 找到那個東西就能反駁。
ABSENCE = [
    r"\bmissing\b",
    r"\bunused\b",
    r"\bundefined\b",
    r"\bundeclared\b",
    r"\bnot (?:being |been )?(?:checked|handled|validated|verified|initiali[sz]ed|defined|declared"
    r"|imported|exported|used|called|invoked|closed|released|freed|awaited|caught|set|reset|cleared"
    r"|updated|propagated|included|registered|found|present|tested|covered|guarded|escaped|saniti[sz]ed)\b",
    r"\bnever (?:be )?(?:used|called|invoked|read|checked|set|initiali[sz]ed|closed|released|freed"
    r"|awaited|assigned|updated)\b",
    r"\b(?:does not|doesn't|do not|don't|did not|didn't|is not|isn't|are not|aren't) (?:check|handle"
    r"|validate|verify|exist|close|release|free|await|catch|initiali[sz]e|reset|clear|update|propagate"
    r"|guard|escape|sanitize|sanitise)\b",
    r"\black(?:s|ing)?\b",
    r"\bno (?:null[- ]check|bounds?[- ]check|check|checks|validation|error[- ]handling|handling|test|tests|guard)\b",
    r"\bwithout (?:checking|validating|verifying|handling|a null[- ]check|null[- ]check|bounds?[- ]check"
    r"|any (?:check|validation))\b",
    r"\bforg(?:ot|ets|otten|etting)\b",
    r"\bomit(?:s|ted)?\b",
]
# 跟 09-21 粗估（missing／unused／not checked／hardcoded…）對照用
BROAD_EXTRA = [r"\bhard[- ]?coded\b"]

ABSENCE_RE = [re.compile(p, re.I) for p in ABSENCE]
BROAD_RE = ABSENCE_RE + [re.compile(p, re.I) for p in BROAD_EXTRA]


def first_hit(note: str, patterns: list[re.Pattern]) -> str:
    for pat in patterns:
        m = pat.search(note)
        if m:
            return m.group(0)
    return ""


def table(rows: list[dict], key: str) -> dict:
    tp = sum(1 for r in rows if r[key] and r["label"] == 0)  # 射程內、錯的
    fp = sum(1 for r in rows if r[key] and r["label"] == 1)  # 射程內、對的
    n0 = sum(1 for r in rows if r["label"] == 0)
    n1 = sum(1 for r in rows if r["label"] == 1)
    base = n1 / (n0 + n1)
    ceiling = n1 / (n0 + n1 - tp)  # 錯的全刪、對的不誤刪
    return {"in_wrong": tp, "in_right": fp, "n_wrong": n0, "n_right": n1, "base": base, "ceiling": ceiling}


def report(name: str, t: dict) -> None:
    ratio = t["in_right"] / t["in_wrong"] if t["in_wrong"] else float("inf")
    print(f"== {name}")
    print(f"   射程內：錯 {t['in_wrong']}/{t['n_wrong']}（{t['in_wrong'] / t['n_wrong']:.1%}）"
          f"、對 {t['in_right']}/{t['n_right']}（{t['in_right'] / t['n_right']:.1%}）、對:錯 = {ratio:.2f}:1")
    print(f"   precision：基準 {t['base']:.2%} → 上限 {t['ceiling']:.2%}（+{(t['ceiling'] - t['base']) * 100:.2f}pp）")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=int, default=0, help="各印 N 則射程內的錯／對 note 供抽查")
    args = ap.parse_args()

    raw = json.loads(DATA.read_text(encoding="utf-8"))
    subset = [r for r in raw if r.get("is_ai_comment") is True and r.get("context") == "Diff Level"]
    rows = []
    for i, r in enumerate(subset):
        note = r.get("note") or ""
        rows.append({
            "idx": i,
            "label": r.get("label"),
            "category": r.get("category"),
            "source_model": r.get("source_model"),
            "absence": first_hit(note, ABSENCE_RE),
            "broad": first_hit(note, BROAD_RE),
            "note": note.replace("\n", " ")[:300],
        })

    n0 = sum(1 for r in rows if r["label"] == 0)
    n1 = sum(1 for r in rows if r["label"] == 1)
    assert (len(rows), n1, n0) == (760, 558, 202), f"子集筆數不符：{len(rows)} / {n1} / {n0}"
    print(f"子集 760 = 正確 {n1} / 錯誤 {n0}（陽性對照通過）\n")

    report("absence（③ 本體）", table(rows, "absence"))
    report("broad（absence ∪ hardcoded，對照 09-21 粗估：錯 13%、對 18%）", table(rows, "broad"))

    # 射程內錯誤 comment 的類別分布
    print("\n== absence 射程內的錯誤 comment，按 category")
    cats: dict[str, int] = {}
    for r in rows:
        if r["absence"] and r["label"] == 0:
            cats[r["category"]] = cats.get(r["category"], 0) + 1
    for c, n in sorted(cats.items(), key=lambda kv: -kv[1]):
        print(f"   {n:3d}  {c}")

    OUT.mkdir(exist_ok=True)
    with (OUT / "reach.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n逐筆結果：{OUT / 'reach.csv'}")

    if args.audit:
        random.seed(20261001)
        for lab, name in ((0, "錯"), (1, "對")):
            pool = [r for r in rows if r["absence"] and r["label"] == lab]
            print(f"\n--- 抽查：absence 射程內、label={lab}（{name}），{min(args.audit, len(pool))} 則 ---")
            for r in random.sample(pool, min(args.audit, len(pool))):
                print(f"- [{r['absence']}] {r['note'][:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
