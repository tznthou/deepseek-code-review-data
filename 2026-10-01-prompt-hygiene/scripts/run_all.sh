#!/bin/bash
# 四輪交錯跑：ph-A1 → ph-B1 → ph-A2 → ph-B2。任一輪失敗就停（不往下跑、不覆寫）。
set -euo pipefail

EXP=<repo>/.claude/experiments
RUN="$EXP/2026-09-24-confidence-loop/scripts/run_round.py"
V="$EXP/2026-10-01-prompt-hygiene/variants"

for label in ph-A1 ph-B1 ph-A2 ph-B2; do
  arm="${label:3:1}"
  # 變數一律加大括號：緊接全形字元時 bash 會把那幾個位元組當成變數名的一部分（10-01 實際撞到）
  echo "=== ${label}（arm ${arm}）開始 $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  python3 "${RUN}" "${label}" "${V}/rubric-${arm}.md" --rules-dir "${V}/rules-${arm}"
  echo "=== ${label} 結束 $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
done
