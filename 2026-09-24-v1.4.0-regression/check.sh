#!/bin/bash
# 對照 expectations.md 的 R1–R7。只 grep 需要的行，不把整份 log 倒出來。
set -u
REPO=tznthou/deepseek-review-probe
COLLECT=36020000495
REVIEW=36020000445
POST=36020030645
S=$(dirname "$0")

gh run view "$COLLECT" --repo "$REPO" --log > "$S/collect.log" 2>/dev/null
gh run view "$POST" --repo "$REPO" --log > "$S/post.log" 2>/dev/null

echo "R1 collect 解析的 tag："
grep -o 'reusable-ai-review-collect.yml@refs/tags/v1 ([0-9a-f]*)' "$S/collect.log" | sort -u
echo "R1 post 解析的 tag："
grep -o 'reusable-ai-review-post.yml@refs/tags/v1 ([0-9a-f]*)' "$S/post.log" | sort -u
echo "R2 kit checkout："
grep -o 'HEAD is now at .*' "$S/post.log" | sort -u
echo "R3/R4 conclusions："
gh run view "$COLLECT" --repo "$REPO" --json conclusion --jq '"collect: " + .conclusion'
gh run view "$REVIEW" --repo "$REPO" --json conclusion,jobs --jq '"code-review: " + .conclusion, (.jobs[] | "  job \(.name): \(.conclusion)")'
echo "R5 post 停在哪："
grep -oE 'HTTP [0-9]{3}[^"]{0,60}' "$S/post.log" | sort -u | head -3
echo "R6 filter-findings no-op 的 ##[warning]："
grep -c '##\[warning\].*filter-findings' "$S/post.log"
echo "R7 送出前掃描（應為 0 行）："
grep -c '送出前掃描' "$S/post.log"
echo "附記 rubric："
grep -oE '使用(呼叫方的自訂|kit 內建) rubric[^"]{0,30}' "$S/post.log" | sort -u
