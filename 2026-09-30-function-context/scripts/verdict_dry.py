#!/usr/bin/env python3
"""score_ctx verdict 的乾跑：fc-1 ← base-1（09-25 舊標籤）、base-3 ← base-2（全標 no）、fc-2 ← base-2。"""
import csv, json, pathlib, sys
sys.dont_write_bytecode = True
E = pathlib.Path("<repo>/.claude/experiments/2026-09-30-function-context")
sys.path.insert(0, str(E / "scripts"))
import score_ctx as s
Q = s.QODO
qidx = lambda pr: Q / "prs" / pr / "pr.diff"
s.ROUNDS = {"base-1": (Q / "rounds/base-1", qidx), "base-2": (Q / "rounds/base-2", qidx),
            "base-3": (Q / "rounds/base-2", qidx), "fc-1": (Q / "rounds/base-1", qidx), "fc-2": (Q / "rounds/base-2", qidx)}
s.BLIND = pathlib.Path(sys.argv[1])
with open(Q / "rounds/base-1/labels.csv", newline="", encoding="utf-8") as fh:
    old = {r["pair"]: r["label"].strip() for r in csv.DictReader(fh)}
mapping, rows, i = {}, [], 0
for run in ("fc-1", "base-3"):
    _, by_pr, fs = s.load(run)
    for p in s.score_bench.pairs_for(fs, by_pr):
        i += 1
        pid = f"P{i:04d}"
        mapping[pid] = {"run": run, "pair": p["pair"], "fid": p["fid"], "gid": p["gid"], "kind": "?",
                        "via": p["via"], "dist": p["dist"], "loc_hit": p["loc_hit"], "conf": 0}
        lab = old.get(p["pair"].replace("fc-1:", "base-1:"), "no") if run == "fc-1" else "no"
        rows.append((pid, lab))
(s.BLIND / "mapping.json").write_text(json.dumps(mapping), encoding="utf-8")
with open(s.BLIND / "labels-part1.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["pair", "label", "note"]); w.writerows([(a, b, "") for a, b in rows])
s.cmd_verdict()
