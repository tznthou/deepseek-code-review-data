# v1.5.0 兩段式發版的 probe 預期表

> 寫於 2026-09-28 01:5x UTC，**`v1.5.0` tag 已推（tag object `fce93b1` → `babdcc6`）、probe 還沒 stage、還沒觸發**。之後不改，結果另外追加。
> 花費預期 $0：probe 的 key 是假值，401 發生在計費之前。
> 這一段只驗得到「不 startup_failure、撈得到規範檔、決定規範檔那步」：一般那步 401 就停，規範那步走不到。規範那步的真跑在 kit 自己的 dogfood（PR-X／PR-Y）。

## Phase P：probe 暫釘 `@v1.5.0`（kit-ref 一起），post 開 `repo-rules-path`，main 上暫放 `.github/review-rules.md`

| # | 預期 | 在哪裡看 |
|---|---|---|
| P1 | collect、post 的 log 寫 `…@refs/tags/v1.5.0 (fce93b1…)` | `gh run view --log` |
| P2 | post 的 kit checkout：`HEAD is now at babdcc6 chore: 發布 v1.5.0 (#48)` | post 的 log |
| P3 | collect：success | `gh run list` |
| P4 | code-review：success（reviewdog、gitleaks、CodeQL Analyze、Trivy 四個 job success；dependency review skipped） | jobs |
| P5 | post：**不是 startup_failure**；conclusion failure，停在一般那步的 HTTP 401 | post 的 log |
| P6 | 「取得呼叫方的自訂 rubric 與規範檔」這步有跑、success | post 的 steps |
| P7 | 「決定規範檔」印出 `repo 規範檔：.github/review-rules.md（…）`，沒有「檔案不存在」的 warning | post 的 log |
| P8 | 「DeepSeek review（repo 規範）」與「貼回 PR」都是 skipped（一般那步先失敗） | post 的 steps |
| P9 | filter-findings no-op 的 `##[warning]` 1 行（舊 caller 相容） | post 的 log |
| P10 | 「送出前掃描」0 行（probe 沒設 REVIEW_BLOCKED_TERMS） | post 的 log |
| P11 | 三個 run 的 `Download action repository` 全部是 `@<40 hex>` | 三份 log |
| P12 | 上傳 artifact 那步有跑（`always()`）；找不到部分檔案的 warning 屬預期 | post 的 steps／log |

## 還原（R）

| # | 預期 |
|---|---|
| R1 | 三支 caller 還原後逐字等於 `probe-orig/` |
| R2 | `.github/review-rules.md` 刪掉，GET 回 404 |

## 結果（追加，2026-09-28 02:00 UTC）

- 觸發：probe `trigger` 分支 commit `96d0777`（01:57:48 UTC）；runs collect `36367972525`、code review `36367972470`、post `36367983838`
- **P1–P12：12/12**（`probe-P-result.txt`）。post 的步驟：撈 caller 與規範檔 success、決定規範檔 success（印出 `repo 規範檔：.github/review-rules.md（…）`）、一般那步 401 failure、規範那步與貼回 skipped、上傳 success
- ⚠️ 第一次判定 11/12（P7 FAIL）是**檢查寫錯**：log 會印出 `run:` 腳本全文，腳本裡本來就寫著「但檔案不存在」那句 warning。改成只認 `##[warning]` 之後同一批 run 重判 12/12；預期表沒改
- **R1、R2 通過**（02:00:30–34 UTC）：三支 caller 逐字還原、規範檔刪除回 404

## Phase F：移 `v1` 之後，probe 原本的 caller（`@v1`、沒設 `repo-rules-path`）

> 寫於 2026-09-28 02:1x UTC，`v1` 已移（02:09:19 UTC，→ `fce93b1`）、Release 已建、#50 已 merge，**觸發之前**。

| # | 預期 |
|---|---|
| F1 | collect、post 的 log 寫 `…@refs/tags/v1 (fce93b1…)` |
| F2 | post 的 kit checkout：`HEAD is now at babdcc6 chore: 發布 v1.5.0 (#48)`（`kit-ref` 用預設 `v1`） |
| F3 | collect：success |
| F4 | code-review：success（四個 job success、dependency review skipped） |
| F5 | post：failure，停在 HTTP 401（不是 startup_failure） |
| F6 | filter-findings no-op 的 `##[warning]` 1 行 |
| F7 | 「送出前掃描」0 行 |
| F8 | 沒設 `repo-rules-path`：「決定規範檔」與「DeepSeek review（repo 規範）」都是 skipped；「取得呼叫方的自訂 rubric 與規範檔」也 skipped（rubric-path 也沒設） |

## Phase F 結果（02:12 UTC）

- 觸發 `2a76f48`（02:12:11 UTC）；runs collect `36368908309`、code review `36368908498`、post `36368923468`
- **F1–F8：8/8**（`probe-F-result.txt`）。沒設 repo-rules-path 的路徑：撈 caller、決定規範檔、規範那步三個都 skipped
- **這次 probe 合計 P 12/12 ＋ R 2/2 ＋ F 8/8 ＝ 22/22，$0**；probe 的 caller 原本就是 `@v1`，F 段不用還原
