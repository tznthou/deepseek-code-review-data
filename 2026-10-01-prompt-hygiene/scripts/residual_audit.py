#!/usr/bin/env python3
"""殘差檢查：抽查發現自動規則會在 PR-A1／PR-X1／PR-X2／PR-B2 套錯標記（10-01 兩批抽查共 7 筆）。
把 8 輪裡「自動標成這四項、沒被人工覆蓋」的 finding 全部拿出來，打亂、換匿名編號，盲著重看。

用法：
  python3 scripts/residual_audit.py count            # 只數，各輪各項幾筆
  python3 scripts/residual_audit.py sheet            # 產生 blind3/ 標記單（含自動標記，跟抽查同格式）
  python3 scripts/residual_audit.py apply            # blind3/blind-labels.csv 有異議的寫回各輪 labels-manual.csv（附加）
"""

import collections
import csv
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
LOOP = HERE.parent / "2026-09-24-confidence-loop"
sys.path.insert(0, str(LOOP / "scripts"))
from label_round import in_range, load_findings  # noqa: E402

ROUNDS = [f"ph-{a}{i}" for i in range(1, 5) for a in "AB"]
ITEMS = {"PR-A1", "PR-X1", "PR-X2", "PR-B2"}
OUT = HERE / "blind3"


def residual() -> list[tuple[dict, str, str]]:
    rules = json.loads((LOOP / "expected-rules.json").read_text(encoding="utf-8"))
    out = []
    for lab in ROUNDS:
        rdir = LOOP / "rounds" / lab
        auto = {r["id"]: r for r in csv.DictReader((rdir / "labels-auto.csv").open(encoding="utf-8"))}
        manual = {r["id"] for r in csv.DictReader((rdir / "labels-manual.csv").open(encoding="utf-8"))}
        for f in load_findings(rdir, list(rules["targets"])):
            a = auto.get(f["id"])
            if a and a["item"] in ITEMS and f["id"] not in manual:
                out.append((f, a["item"], a["label"]))
    return out


def main() -> int:
    mode = sys.argv[1]
    rows = residual()
    if mode == "count":
        c = collections.Counter((f["id"].split(":")[0], item) for f, item, _ in rows)
        for lab in ROUNDS:
            print(lab, {it: c[(lab, it)] for it in sorted(ITEMS)})
        print(f"合計 {len(rows)} 筆")
        return 0

    if mode == "sheet":
        if (OUT / "blind-labels.csv").exists():
            sys.exit(f"[停] {OUT} 已經有標記檔，不覆寫")
        rules = json.loads((LOOP / "expected-rules.json").read_text(encoding="utf-8"))
        notes = {it["id"]: it["note"] for it in rules["items"]}
        random.seed(20261002)
        random.shuffle(rows)
        mapping, sheet = {}, ["# 殘差盲標單（自動標記；同意就不用寫，有異議才寫進 blind-labels.csv）", ""]
        for k, (f, item, lb) in enumerate(rows, 1):
            code = f"R{k:03d}"
            mapping[code] = f["id"]
            try:
                line = int(f.get("line"))
            except (TypeError, ValueError):
                line = -99
            cands = [it["id"] for it in rules["items"] if it["target"] == f["target"] and in_range(line, it["lines"])]
            sheet += [f"## {code} ｜ 標的 {f['target']} ｜ `{f.get('path')}:{f.get('line')}` ｜ 自動：{item} → {lb}", "",
                      f"**{f.get('title', '')}**", "", f"body：{f.get('body', '')}", ""]
            sheet += [f"- 規則提示 {c}：{notes[c]}" for c in cands] + [""]
        OUT.mkdir(exist_ok=True)
        (OUT / "blind-sheet.md").write_text("\n".join(sheet), encoding="utf-8")
        (OUT / "blind-map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
        with (OUT / "blind-labels.csv").open("w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerow(["code", "item", "label", "reason"])
        print(f"{len(rows)} 筆 → {OUT / 'blind-sheet.md'}")
        return 0

    if mode == "apply":
        mapping = json.loads((OUT / "blind-map.json").read_text(encoding="utf-8"))
        per_round = collections.defaultdict(list)
        for r in csv.DictReader((OUT / "blind-labels.csv").open(encoding="utf-8")):
            fid = mapping[r["code"]]
            per_round[fid.split(":", 1)[0]].append({"id": fid, "item": r["item"], "label": r["label"], "reason": r["reason"]})
        for lab, items in sorted(per_round.items()):
            path = LOOP / "rounds" / lab / "labels-manual.csv"
            with path.open("a", encoding="utf-8", newline="") as fh:
                csv.DictWriter(fh, fieldnames=["id", "item", "label", "reason"]).writerows(items)
            print(f"{lab}: 附加 {len(items)} 筆覆蓋")
        return 0
    sys.exit(f"不認得的模式：{mode}")


if __name__ == "__main__":
    raise SystemExit(main())
