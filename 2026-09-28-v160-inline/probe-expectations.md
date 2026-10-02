# v1.6.0 兩段式發版的 probe 預期表

> 寫於 2026-09-28 06:08 UTC，**`v1.6.0` tag 已推（tag object `40c2a78` → `49a5975`）、`v1` 仍在 v1.5.0（`fce93b1`）、
> probe 還沒 stage、還沒觸發**。之後不改，結果另外追加。
> 花費預期 $0：probe 的 key 是假值，401 發生在計費之前。
> 這一段只驗得到「傳了新 input 不會 startup_failure、kit 抓到的是 v1.6.0」：一般那步 401 就停，貼文那步走不到，
> `--no-inline` 有沒有帶在這裡看不到。預設路徑（不傳 input）與真的貼文，由本 repo 的 `04` 暫釘 `@v1.6.0` 用真 API 驗。

## Phase P：probe 暫釘 `@v1.6.0`（kit-ref 一起），post 傳 `inline-comments: true`

| # | 預期 | 在哪裡看 |
|---|---|---|
| P1 | collect、post 的 log 寫 `…@refs/tags/v1.6.0 (40c2a78…)` | `gh run view --log` |
| P2 | post 的 kit checkout：`HEAD is now at 49a5975 chore: 發布 v1.6.0 (#55)` | post 的 log |
| P3 | collect：success | `gh run list` |
| P4 | code-review：success（reviewdog、gitleaks、CodeQL Analyze、Trivy 四個 job success；dependency review skipped） | jobs |
| P5 | post：**不是 startup_failure**（傳了 `inline-comments: true`）；conclusion failure，停在一般那步的 HTTP 401 | post 的 log |
| P6 | 「取得呼叫方的自訂 rubric 與規範檔」skipped（rubric-path、repo-rules-path 都沒設） | post 的 steps |
| P7 | 「決定規範檔」與「DeepSeek review（repo 規範）」都 skipped | post 的 steps |
| P8 | 「貼回 PR（摘要 + inline comments）」skipped（一般那步先失敗） | post 的 steps |
| P9 | filter-findings no-op 的 `##[warning]` 1 行（舊 caller 相容） | post 的 log |
| P10 | 「送出前掃描」0 行（probe 沒設 REVIEW_BLOCKED_TERMS） | post 的 log |
| P11 | 三個 run 的 `Download action repository` 全部是 `@<40 hex>` | 三份 log |
| P12 | 上傳 artifact 那步有跑（`always()`） | post 的 steps |

## 還原（R）

| # | 預期 |
|---|---|
| R1 | 三支 caller 還原後逐字等於 `probe-orig/` |

## Phase F：移 `v1` 之後，probe 原本的 caller（`@v1`、沒傳 `inline-comments`）

> 寫於 2026-09-28 06:20 UTC，`v1` 已移（06:19:10 UTC，→ `40c2a78`）、Release 已建、#57 已 merge，**觸發之前**。

| # | 預期 |
|---|---|
| F1 | collect、post 的 log 寫 `…@refs/tags/v1 (40c2a78…)` |
| F2 | post 的 kit checkout：`HEAD is now at 49a5975 chore: 發布 v1.6.0 (#55)`（`kit-ref` 用預設 `v1`） |
| F3 | collect：success |
| F4 | code-review：success（四個 job success、dependency review skipped） |
| F5 | post：failure，停在 HTTP 401（不是 startup_failure；沒傳新 input 的舊 caller 照樣能跑） |
| F6 | filter-findings no-op 的 `##[warning]` 1 行 |
| F7 | 「送出前掃描」0 行 |
| F8 | 沒設 `repo-rules-path`：「取得呼叫方的自訂 rubric 與規範檔」「決定規範檔」「DeepSeek review（repo 規範）」都 skipped |
