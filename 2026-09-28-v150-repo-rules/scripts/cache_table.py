#!/usr/bin/env python3
"""從 04 的 log 撈兩次呼叫的 prompt／cached token 與時間，印成一張表。"""
import json
import pathlib
import re
import sys
from datetime import datetime

SCRATCH = pathlib.Path(__file__).parent.parent / "cache-logs"
RUNS = sys.argv[1:]
TS = re.compile(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+)Z ")


def ts(line: str) -> datetime:
    m = TS.search(line)
    return datetime.fromisoformat(m.group(1)[:26])


for run in RUNS:
    lines = (SCRATCH / f"run-{run}.log").read_text(encoding="utf-8", errors="replace").splitlines()
    calls = [l for l in lines if "[info] 呼叫 " in l]
    dones = [l for l in lines if "[info] 完成於" in l]
    rows = []
    for c, d in zip(calls, dones):
        usage = json.loads(d.split("usage=", 1)[1])
        rows.append((ts(c), ts(d), usage["prompt_tokens"], usage.get("prompt_tokens_details", {}).get("cached_tokens")))
    if len(rows) != 2:
        print(run, "呼叫數不是 2：", len(rows))
        continue
    (s1, e1, p1, c1), (s2, e2, p2, c2) = rows
    gap_end_start = (s2 - e1).total_seconds()
    gap_start_start = (s2 - s1).total_seconds()
    print(
        f"{run}  一般 prompt={p1:5d} cached={c1:5d} ｜ 規範 prompt={p2:5d} cached={c2:5d} "
        f"(一般整段取 64 倍數={p1 // 64 * 64}) ｜ 間隔 結束→開始 {gap_end_start:.2f}s、開始→開始 {gap_start_start:.1f}s"
    )
