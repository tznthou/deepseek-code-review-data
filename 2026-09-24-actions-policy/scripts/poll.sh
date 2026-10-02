#!/bin/bash
# usage: poll.sh <T0 ISO UTC> [max_sec]
# 等 T0 之後建立的 collect / code review 兩支跑完，再最多等 120 秒看 post 會不會出現並跑完
T0="$1"; MAX="${2:-720}"; start=$(date +%s); grace=0
while :; do
  runs=$(gh run list --repo tznthou/deepseek-review-probe --limit 15 --json databaseId,workflowName,status,conclusion,event,createdAt,updatedAt,headSha \
    --jq "[.[] | select(.createdAt >= \"$T0\")]")
  done2=$(echo "$runs" | jq '[.[] | select((.workflowName=="ai review collect" or .workflowName=="code review") and .status=="completed")] | length')
  post=$(echo "$runs" | jq -r '[.[] | select(.workflowName=="ai review post")] | if length==0 then "none" else .[0].status end')
  now=$(date +%s)
  if [ "$done2" -ge 2 ]; then
    if [ "$post" = "completed" ]; then break; fi
    grace=$((grace+10)); if [ $grace -ge 120 ]; then echo "(post 在 collect/code-review 跑完後 120 秒內沒有跑完或沒出現: $post)"; break; fi
  fi
  if [ $((now-start)) -ge "$MAX" ]; then echo "(TIMEOUT ${MAX}s)"; break; fi
  sleep 10
done
echo "$runs" | jq -r '.[] | "\(.databaseId)\t\(.workflowName)\t\(.event)\t\(.status)\t\(.conclusion)\t\(.createdAt)\t\(.updatedAt)\t\(.headSha[0:7])"'
