#!/bin/bash
# 追加的四輪：ph-A3 → ph-B3 → ph-A4 → ph-B4（跑前定稿見 README「追加」）。任一輪失敗就停。
set -euo pipefail

EXP=<repo>/.claude/experiments
RUN="${EXP}/2026-09-24-confidence-loop/scripts/run_round.py"
V="${EXP}/2026-10-01-prompt-hygiene/variants"

for label in ph-A3 ph-B3 ph-A4 ph-B4; do
  arm="${label:3:1}"
  echo "=== ${label}（arm ${arm}）開始 $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  python3 "${RUN}" "${label}" "${V}/rubric-${arm}.md" --rules-dir "${V}/rules-${arm}"
  echo "=== ${label} 結束 $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
done
