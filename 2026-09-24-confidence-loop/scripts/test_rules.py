#!/usr/bin/env python3
"""拿今天手動盲標過的 S（09-21 flash-3x 的 v4-pro 6 次跑、41 筆）驗證 expected-rules.json。

做法：把那 6 次跑的 JSON 放進 rounds/_ruletest/，跑 label_round.py，比對自動標記與
labels-S.csv 的人工標記。自動標記跟人工不一致 → 規則要先修，不能 hash 鎖住。
（shell 那 3 次是舊版 B2 的標的，但除了第 68 行內容，行號與內容都一樣。）
"""
import csv
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOOP = HERE.parent
OLD = LOOP.parent / "2026-09-21-flash-3x/runs"
RD = LOOP / "rounds/_ruletest"

# 09-21 的跑 → 今天盲標單的 S 編號（extract_seeded.py 的順序：py-3way 9 筆之後）
ORDER = [("python", i, f"python--deepseek-v4-pro--{i}.json") for i in (1, 2, 3)]
ORDER += [("shell", i, f"shell--deepseek-v4-pro--{i}.json") for i in (1, 2, 3)]

if RD.exists():
    shutil.rmtree(RD)
RD.mkdir(parents=True)
sid = 9
mapping = {}
results = []
for target, run, name in ORDER:
    items = json.loads((OLD / name).read_text(encoding="utf-8"))
    shutil.copy(OLD / name, RD / f"{target}-{run}.json")
    results.append({"target": target, "run": run, "exit": 0, "findings": len(items)})
    for k in range(1, len(items) + 1):
        sid += 1
        mapping[f"_ruletest:{target}:{run}:{k}"] = f"S{sid:02d}"
(RD / "manifest.json").write_text(json.dumps({"runs": 3, "results": results}), encoding="utf-8")

subprocess.run([sys.executable, str(HERE / "label_round.py"), "_ruletest"], check=True)

human = {}
with open(LOOP / "labels-S.csv", encoding="utf-8") as fh:
    for line in fh.read().splitlines()[1:]:
        sid_, lab = line.split(",", 3)[:2]
        human[sid_] = lab
with open(RD / "labels-auto.csv", encoding="utf-8", newline="") as fh:
    auto = {r["id"]: r for r in csv.DictReader(fh)}
manual = (RD / "manual-ids.txt").read_text(encoding="utf-8").split()

agree, disagree = 0, []
for fid, row in auto.items():
    h = human[mapping[fid]]
    if row["label"] == h:
        agree += 1
    else:
        disagree.append(f"{mapping[fid]}（{fid}）自動 {row['item']}→{row['label']}，人工 {h}")
print(f"\n自動 {len(auto)} 筆：一致 {agree}、不一致 {len(disagree)}；人工 {len(manual)} 筆")
for d in disagree:
    print("  ✗ " + d)
print("  人工那幾筆：" + ", ".join(f"{mapping[m]}={human[mapping[m]]}" for m in manual))
sys.exit(1 if disagree else 0)
