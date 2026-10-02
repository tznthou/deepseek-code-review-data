#!/bin/bash
# usage: inspect.sh <run_id> —— 一個 run 的原因分別在哪裡看得到
R=tznthou/deepseek-review-probe; id="$1"; L="$(cd "$(dirname "$0")" && pwd)/log-$id.txt"
echo "######## run $id"
gh api "repos/$R/actions/runs/$id" --jq '"name=\(.name) event=\(.event) status=\(.status) conclusion=\(.conclusion) check_suite=\(.check_suite_id) run_attempt=\(.run_attempt)"'
echo "---- (a) gh run view"
gh run view "$id" --repo "$R" 2>&1 | head -40
echo "---- (b) gh run view --log-failed (前 30 行 + 含 not allowed/pinned 的行)"
gh run view "$id" --repo "$R" --log-failed > "$L" 2>&1; echo "log lines: $(wc -l < "$L")"; head -30 "$L" | cut -c1-300; grep -n -i 'not allowed\|pinned\|full-length' "$L" | cut -c1-400 | head -10
echo "---- (c) jobs + check-run annotations"
gh api "repos/$R/actions/runs/$id/jobs?per_page=50" --jq '.total_count as $n | "jobs=\($n)", (.jobs[] | "\(.id)\t\(.name)\t\(.status)\t\(.conclusion)")'
for cr in $(gh api "repos/$R/actions/runs/$id/jobs?per_page=50" --jq '.jobs[].id'); do
  gh api "repos/$R/check-runs/$cr/annotations" --jq '.[] | "  [ann \(.annotation_level)] \(.path):\(.start_line) \(.message|gsub("\n";" ")|.[0:400])"' 2>&1
done
echo "---- (d) check suite 的 check-runs"
cs=$(gh api "repos/$R/actions/runs/$id" --jq '.check_suite_id'); gh api "repos/$R/check-suites/$cs/check-runs" --jq '"check_runs=\(.total_count)", (.check_runs[] | "\(.name)\t\(.status)\t\(.conclusion)\tann=\(.output.annotations_count)\t\(.output.title // "")")' 2>&1
