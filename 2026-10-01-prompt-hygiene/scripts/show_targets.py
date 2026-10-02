#!/usr/bin/env python3
"""把三個標的的 diff 還原成帶行號的新檔內容（標記時對照用）。標的都是 @@ -0,0 +1,N @@ 的整檔新增。"""

import json
import pathlib

LOOP = pathlib.Path(__file__).resolve().parents[2] / "2026-09-24-confidence-loop"
rules = json.loads((LOOP / "expected-rules.json").read_text(encoding="utf-8"))
out = pathlib.Path(__file__).resolve().parent.parent / "targets-view"
out.mkdir(exist_ok=True)
for target, spec in rules["targets"].items():
    lines = (LOOP / spec["diff"]).read_text(encoding="utf-8").split("\n")
    body = [ln[1:] for ln in lines if ln.startswith("+") and not ln.startswith("+++")]
    text = "\n".join(f"{i:4d}  {ln}" for i, ln in enumerate(body, 1))
    (out / f"{target}.txt").write_text(text + "\n", encoding="utf-8")
    print(f"{target}: {spec['diff']} → {len(body)} 行")
