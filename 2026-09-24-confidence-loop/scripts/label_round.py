#!/usr/bin/env python3
"""依 expected-rules.json 替一輪的 finding 提出標記。

- 規則能唯一判定的 → labels-auto.csv
- 判不了的（沒有候選、多個候選、unless 命中、auto=false）→ manual-sheet.md，
  **盲標**：不列 confidence、不列 severity，標完才由 analyze_round.py join
- 自動標記每 8 筆抽 1 筆，連同自動給的標記一起列進 manual-sheet.md 的「抽查」段，
  人工複核；複核結果寫進 labels-manual.csv 就會覆蓋自動標記

用法：label_round.py <輪次標籤>
"""
import csv
import json
import pathlib
import re
import sys

LOOP = pathlib.Path(__file__).resolve().parents[1]
TOL = 2
SPOT_EVERY = 8


def load_findings(rdir: pathlib.Path, targets: list[str]) -> list[dict]:
    out = []
    for target in targets:
        for path in sorted(rdir.glob(f"{target}-*.json")):
            run = int(path.stem.rsplit("-", 1)[1])
            try:
                items = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for k, f in enumerate(items, 1):
                out.append({**f, "id": f"{rdir.name}:{target}:{run}:{k}", "target": target, "run": run})
    return out


def in_range(line: int, ranges: list[list[int]]) -> bool:
    return any(lo - TOL <= line <= hi + TOL for lo, hi in ranges)


def main() -> None:
    label = sys.argv[1]
    rdir = LOOP / "rounds" / label
    rules = json.loads((LOOP / "expected-rules.json").read_text(encoding="utf-8"))
    findings = load_findings(rdir, list(rules["targets"]))

    key = {f["id"]: {"confidence": float(f["confidence"]), "severity": f["severity"]} for f in findings}
    (rdir / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")

    auto_rows, manual, spot = [], [], []
    for f in findings:
        text = f"{f.get('title', '')}\n{f.get('body', '')}"
        try:
            line = int(f.get("line"))
        except (TypeError, ValueError):
            line = -99
        cands = [it for it in rules["items"] if it["target"] == f["target"] and in_range(line, it["lines"])]
        hits, forced = [], []
        for it in cands:
            if not re.search(it["match"], text):
                continue
            if it.get("unless") and re.search(it["unless"], text):
                forced.append(it["id"] + "(unless)")
            elif not it["auto"] or it["label"] == "manual":
                forced.append(it["id"])
            else:
                hits.append(it)
        if len(hits) == 1 and not forced:
            auto_rows.append({"id": f["id"], "item": hits[0]["id"], "label": hits[0]["label"]})
            if len(auto_rows) % SPOT_EVERY == 0:
                spot.append((f, hits[0]))
        else:
            reason = "候選：" + (", ".join([h["id"] for h in hits] + forced) or "無")
            manual.append((f, reason, [it["id"] for it in cands]))

    with open(rdir / "labels-auto.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "item", "label"])
        w.writeheader()
        w.writerows(auto_rows)

    notes = {it["id"]: it["note"] for it in rules["items"]}
    sheet = [f"# {label} 人工標記單（盲標：不含 confidence、severity）", "",
             f"自動 {len(auto_rows)} 筆、人工 {len(manual)} 筆、抽查 {len(spot)} 筆。",
             "結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。", ""]

    def block(f: dict, header: str) -> list[str]:
        return [f"## {f['id']} ｜ `{f.get('path')}:{f.get('line')}` ｜ {header}", "",
                f"**{f.get('title', '')}**", "", "existing_code:", "```",
                str(f.get("existing_code", "")), "```", "", f"body：{f.get('body', '')}", "",
                f"evidence：{f.get('evidence', '')}", ""]

    sheet += ["# 需要人工判定", ""]
    for f, reason, cand_ids in manual:
        sheet += block(f, reason)
        sheet += [f"- 規則提示 {c}：{notes[c]}" for c in cand_ids] + [""]
    sheet += ["# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）", ""]
    for f, it in spot:
        sheet += block(f, f"自動：{it['id']} → {it['label']}")
    (rdir / "manual-sheet.md").write_text("\n".join(sheet), encoding="utf-8")
    manual_ids = [f["id"] for f, _, _ in manual]
    (rdir / "manual-ids.txt").write_text("\n".join(manual_ids) + "\n", encoding="utf-8")
    print(f"{label}: findings {len(findings)}｜自動 {len(auto_rows)}｜人工 {len(manual)}｜抽查 {len(spot)}")


if __name__ == "__main__":
    main()
