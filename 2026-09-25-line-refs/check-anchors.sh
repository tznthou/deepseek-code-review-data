#!/bin/bash
# 每個錨點在目標檔裡必須剛好出現一次（-F 字面比對）
W=<repo>/.github/workflows
fail=0
check() {
  local file="$1" anchor="$2"
  local n
  n=$(/usr/bin/grep -c -F -- "$anchor" "$W/$file")
  if [ "$n" = "1" ]; then
    echo "OK   $file :: $anchor"
  else
    echo "FAIL $file :: $anchor  (出現 $n 次)"
    fail=1
  fi
}
check 04-ai-review-post.yml "workflows: ['03 ai review collect']"
check 01-static-review.yml "# TODO: 換成你的 linter"
check 02-codeql.yml "language: [python]"
check 02-codeql.yml "build-mode: none"
echo "---"
echo "SETUP-CHECKLIST 裡提到「行號」的地方："
/usr/bin/grep -n '行號' <repo>/SETUP-CHECKLIST.md
exit $fail
