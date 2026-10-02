#!/bin/bash
# 對照 expectations.md（S1–S9 / E2–E5 / F1–F7）。只 grep 需要的行，不把整份 log 倒出來。
# usage: check.sh <phase> <collect_run> <review_run> <post_run>
set -u
REPO=tznthou/deepseek-review-probe
PHASE="$1"; COLLECT="$2"; REVIEW="$3"; POST="$4"
D="$(cd "$(dirname "$0")" && pwd)/logs"
mkdir -p "$D"
gh run view "$COLLECT" --repo "$REPO" --log > "$D/$PHASE-collect.log" 2>/dev/null
gh run view "$REVIEW" --repo "$REPO" --log > "$D/$PHASE-review.log" 2>/dev/null
gh run view "$POST" --repo "$REPO" --log > "$D/$PHASE-post.log" 2>/dev/null
ALL=("$D/$PHASE-collect.log" "$D/$PHASE-review.log" "$D/$PHASE-post.log")

echo "[1] 解析到的 reusable 與 tag："
grep -ohE "reusable-[a-z-]+\.yml@refs/tags/[^ ]+ \([0-9a-f]+\)" "${ALL[@]}" | LC_ALL=C sort | uniq -c
echo "[2] post 的 kit checkout："
grep -oE 'HEAD is now at .*' "$D/$PHASE-post.log" | LC_ALL=C sort -u
echo "[3/4] conclusions："
gh run view "$COLLECT" --repo "$REPO" --json conclusion --jq '"  collect: " + .conclusion'
gh run view "$REVIEW" --repo "$REPO" --json conclusion,jobs --jq '"  code-review: " + .conclusion, (.jobs[] | "    job \(.name): \(.conclusion)")'
gh run view "$POST" --repo "$REPO" --json conclusion --jq '"  post: " + .conclusion'
echo "[5] post 停在哪："
grep -oE 'HTTP [0-9]{3}[^"]{0,60}' "$D/$PHASE-post.log" | LC_ALL=C sort -u | head -3
echo "[6] filter-findings 的 ##[warning]（應為 1）："
grep -c '##\[warning\].*filter-findings' "$D/$PHASE-post.log"
echo "[7] 送出前掃描（應為 0）："
grep -c '送出前掃描' "$D/$PHASE-post.log"
echo "[8] Download action repository：SHA 引用的種類數，以及非 SHA 的（應為空）："
grep -ohE "Download action repository '[^']+'" "${ALL[@]}" | LC_ALL=C sort -u | grep -cE "@[0-9a-f]{40}'"
grep -ohE "Download action repository '[^']+'" "${ALL[@]}" | LC_ALL=C sort -u | grep -vE "@[0-9a-f]{40}'"
echo "[9] reviewdog 的 LINT_NAME："
grep -oE 'LINT_NAME: [A-Za-z0-9_-]+' "$D/$PHASE-review.log" | LC_ALL=C sort -u
echo "[E5] must be pinned（應為 0）："
cat "${ALL[@]}" | grep -c 'must be pinned to a full-length commit SHA'
