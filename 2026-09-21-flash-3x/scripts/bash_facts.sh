#!/bin/bash
# 兩條 bash 行為實測：grep -c . 在各種 log 內容下的輸出；if 條件裡的 [ 失敗會不會觸發 set -e
D=$(mktemp -d)
printf '' > "$D/empty"
printf '\n\n' > "$D/newlines"
printf '   \n' > "$D/spaces"
printf 'a\n' > "$D/one"
for f in missing empty newlines spaces one; do
  total=$(grep -c . "$D/$f" 2>/dev/null || echo 0)
  printf '%-9s total=%q  ' "$f" "$total"
  if [ "$total" -gt 100 ] 2>/dev/null; then echo '[ ] 真'; else echo "[ ] rc=$?"; fi
done
echo "--- set -e + if [ \"\" -gt 0 ]"
bash -c 'set -e; if [ "" -gt 0 ]; then echo yes; fi; echo continued' 2>&1
echo "--- 沒有 set -e"
bash -c 'if [ "" -gt 0 ]; then echo yes; fi; echo continued' 2>&1
echo "bash $BASH_VERSION"
rm -rf "$D"
