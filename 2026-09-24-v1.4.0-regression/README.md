# v1.4.0 發版後的 probe 回歸（2026-09-24）

> 狀態：**7/7 符合預期，$0**。預期表 `expectations.md`：打 tag 之前寫好，tag object 與 merge commit 的 SHA 在觸發之前填入。

- 發版：PR #35（rubric 改動，squash `9d0dfa2`）→ PR #36（`chore: 發布 v1.4.0`，squash `fa37001`，15:23:43 UTC）
- tag：`v1.4.0` = `23023b4`（annotated）→ `fa37001`；`v1` 跟著改指向 `23023b4`（push `-f`）；Release 只建在 `v1.4.0`，而且是 Latest
- 觸發：probe `trigger` 分支 commit `db3fd45`（15:24:47 UTC，contents API，`commit.py`）

| # | 結果 | 證據 |
|---|---|---|
| R1 | ✅ | collect 和 post 都是 `@refs/tags/v1 (23023b4…)` |
| R2 | ✅ | `HEAD is now at fa37001 chore: 發布 v1.4.0 (#36)` |
| R3 | ✅ | collect `36020000495` success |
| R4 | ✅ | code review `36020000445` success：gitleaks、Analyze、Trivy、reviewdog 都 success，dependency review 是 skipped |
| R5 | ✅ | post `36020030645` 停在 HTTP 401 |
| R6 | ✅ | 1 行 `##[warning]`（filter-findings no-op） |
| R7 | ✅ | 「送出前掃描」0 行 |

附記：post 實際印出的是「使用 kit 內建 rubric」（post.log 第 209 行），所以 probe 跑的是 v1.4.0 的新 rubric。
⚠️ `check.sh` 的附記那行 grep 沒把這一行印出來，只抓到 log 裡 script 原文的 `$CUSTOM`。這是直接 grep 才確認的，下次別信 check.sh 的附記那一行。

腳本：`commit.py`（從 actions-policy 實驗複製過來，註解字樣改成 `regression`）、`poll.sh`、`check.sh`。
