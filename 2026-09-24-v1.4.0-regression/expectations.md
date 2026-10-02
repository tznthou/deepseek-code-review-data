# v1.4.0 發版後的 probe 回歸：預期表

> 寫於打 tag 之前。tag object 的 SHA 在打完 tag、觸發之前補進來；其餘項目觸發之前就定稿，之後不改。
> 對照基準：09-23 `v1.3.1` 的回歸（commit `7869a51`，7/7）。

| # | 預期 | 在哪裡看 |
|---|---|---|
| R1 | collect、post 的 log 都寫 `Uses: …@refs/tags/v1 (<v1.4.0 tag object>)` | `gh run view --log` |
| R2 | kit checkout 到發版的 merge commit：`HEAD is now at <merge commit> chore: 發布 v1.4.0 (#36)` | post 的 log |
| R3 | collect：success | `gh run list` |
| R4 | code-review：success（reviewdog、gitleaks、CodeQL Analyze、Trivy 四個 job 都 success；dependency review 是 skipped） | jobs |
| R5 | post：failure，停在 HTTP 401（probe 的 key 是假值） | post 的 log |
| R6 | post 的 log 有 filter-findings no-op 的 `##[warning]`（probe 刻意傳 `filter-findings: true`） | post 的 log |
| R7 | 沒有設 `REVIEW_BLOCKED_TERMS`，所以沒有「送出前掃描」那一行 | post 的 log |

額外記錄（不計分）：post 的 log 裡「使用 kit 內建 rubric」那一行；花費預期 $0（401 在計費之前）。

v1.4.0 tag object：`23023b4`（`23023b4d64e6015f9dc34a562a8cb023875b61e7`）
發版 merge commit：`fa37001`（`fa37001fb36f9001148fe1063ddc58ed31611a79`）
→ R1 要看到 `@refs/tags/v1 (23023b4…)`；R2 要看到 `HEAD is now at fa37001 chore: 發布 v1.4.0 (#36)`
