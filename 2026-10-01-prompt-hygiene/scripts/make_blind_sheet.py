#!/usr/bin/env python3
"""把四輪要人工判定的 finding 合併、打亂、換匿名編號，標記時看不出是 A 組還是 B 組。

先對每輪跑過 label_round.py（產生 manual-ids.txt 與 manual-sheet.md），再跑這支：
  python3 scripts/make_blind_sheet.py ph-A1 ph-B1 ph-A2 ph-B2
產出（實驗目錄 blind/）：
  blind-sheet.md   標記單：不含 confidence、severity、輪次名
  blind-map.json   匿名編號 → 原 id（標完之前不要打開）
  blind-labels.csv 空白表頭（code,item,label,reason），標完交給 unblind.py
"""

import csv
import json
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
LOOP = HERE.parent / "2026-09-24-confidence-loop"
sys.path.insert(0, str(LOOP / "scripts"))
from label_round import in_range, load_findings  # noqa: E402

SPOT_RE = re.compile(r"^## (\S+) ｜ .* ｜ 自動：(\S+) → (\S+)$", re.M)


def main() -> int:
    args = sys.argv[1:]
    # 第二批用 --dir blind2，不要蓋掉第一批的 blind/
    out_name = "blind"
    if args[:1] == ["--dir"]:
        out_name, args = args[1], args[2:]
    labels = args
    rules = json.loads((LOOP / "expected-rules.json").read_text(encoding="utf-8"))
    notes = {it["id"]: it["note"] for it in rules["items"]}
    targets = list(rules["targets"])

    manual, spot = [], []
    for lab in labels:
        rdir = LOOP / "rounds" / lab
        by_id = {f["id"]: f for f in load_findings(rdir, targets)}
        ids = [x for x in (rdir / "manual-ids.txt").read_text(encoding="utf-8").split("\n") if x]
        manual += [by_id[i] for i in ids]
        for fid, item, lb in SPOT_RE.findall((rdir / "manual-sheet.md").read_text(encoding="utf-8")):
            spot.append((by_id[fid], item, lb))

    random.seed(20261001)
    random.shuffle(manual)
    random.shuffle(spot)
    mapping: dict[str, str] = {}

    def block(code: str, f: dict, header: str) -> list[str]:
        mapping[code] = f["id"]
        try:
            line = int(f.get("line"))
        except (TypeError, ValueError):
            line = -99
        cands = [it["id"] for it in rules["items"] if it["target"] == f["target"] and in_range(line, it["lines"])]
        out = [f"## {code} ｜ 標的 {f['target']} ｜ `{f.get('path')}:{f.get('line')}` ｜ {header}", "",
               f"**{f.get('title', '')}**", "", "existing_code:", "```", str(f.get("existing_code", "")), "```", "",
               f"body：{f.get('body', '')}", "", f"evidence：{f.get('evidence', '')}", ""]
        return out + [f"- 規則提示 {c}：{notes[c]}" for c in cands] + [""]

    sheet = ["# 盲標單（不含 confidence、severity、輪次）", "",
             f"人工 {len(manual)} 筆、抽查 {len(spot)} 筆。結果寫進 blind-labels.csv（code,item,label,reason）。",
             "label 只能是 valid／invalid／disputed；item 寫 expected-rules 的 id，對不到就寫 NONE。", "",
             "# 需要人工判定", ""]
    for k, f in enumerate(manual, 1):
        sheet += block(f"M{k:03d}", f, "人工")
    sheet += ["# 抽查（自動標記；同意就不用寫，有異議才寫進 blind-labels.csv）", ""]
    for k, (f, item, lb) in enumerate(spot, 1):
        sheet += block(f"S{k:03d}", f, f"自動：{item} → {lb}")

    out = HERE / out_name
    if (out / "blind-labels.csv").exists():
        sys.exit(f"[停] {out} 已經有標記檔，不覆寫")
    out.mkdir(exist_ok=True)
    (out / "blind-sheet.md").write_text("\n".join(sheet), encoding="utf-8")
    (out / "blind-map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    with (out / "blind-labels.csv").open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerow(["code", "item", "label", "reason"])
    print(f"人工 {len(manual)} 筆、抽查 {len(spot)} 筆 → {out / 'blind-sheet.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
