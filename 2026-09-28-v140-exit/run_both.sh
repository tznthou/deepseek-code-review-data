#!/bin/bash
# v131-1 跑完才跑 v131-2（第二輪吃第一輪的快取）。run_bench 可續跑：已成功的 PR 會跳過。
set -u
cd <repo> || exit 1
D=.claude/experiments/2026-09-28-v140-exit
R=.claude/experiments/2026-09-25-qodo-bench/scripts/run_bench.py
export PYTHONDONTWRITEBYTECODE=1
python3 "$R" v131-1 --rubric "$D/rubric-v1.3.1.md" && python3 "$R" v131-2 --rubric "$D/rubric-v1.3.1.md"
echo "EXIT=$?"
