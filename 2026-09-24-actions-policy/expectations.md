# 預期表（2026-09-24 12:10 UTC 定稿，在 E1 觸發之前；跑完不改）

基準（09-23 那次，`all`／不強制 SHA）：collect success、code-review success、post failure（假 key → 401，停在 API 呼叫）。
每一組和基準比只改了政策這一個變數。所以 conclusion 跟基準不同，就算作「被政策擋下」；原因文字看不看得到另外記。

信心是寫這張表時自己估的，不是量出來的。

## E1：`local_only`

| # | 預期 | 信心 | 依據 |
|---|---|---|---|
| E1-1 | collect **不是** success | 高 | 文件明寫 local_only 擋 `actions/checkout` |
| E1-2 | conclusion 是 `startup_failure`（驗收 AI 也這麼說） | 低（約五成） | kit reusable 裡最外層的 `uses:` 在解析時就看得到，猜政策在建立 run 時就檢查 |
| E1-3 | 被點名的是 `actions/checkout@v7` 這類 GitHub 官方 action，**不是** kit 的 reusable workflow（U4 = OWNER 涵蓋同帳號的其他 repo；U1 = 政策會套到 reusable 裡面） | 中 | UI 的選項名稱是「Allow *OWNER* …」，個人帳號的 OWNER 就是帳號本身 |
| E1-4 | code-review 同樣被擋，conclusion 和 E1-2 同型 | 中 | 兩支 reusable 都用 `actions/checkout` |
| E1-5 | post 會被觸發，然後同樣被擋 | 低 | 不確定 startup_failure 的 run 會不會觸發 `workflow_run: completed` |
| E1-6 | 原因用 CLI 看不到：`gh run view` 沒有原因、`--log-failed` 沒有 log、check-run annotations 是空的 | 中低 | RESUME 記過：漏 permissions 造成的 startup_failure，CLI 一樣查不出原因 |

## E2：`selected` + GitHub 官方 + 三條 pattern（reviewdog／gitleaks／trivy）

前提是 E1-3 成立。如果不成立，照 README 先登記的分支加上 kit 的 pattern，下面的預期不變。

| # | 預期 | 信心 | 依據 |
|---|---|---|---|
| E2-1 | collect success | 中高 | 只用 `actions/*`，而 kit 屬於 OWNER |
| E2-2 | post 和基準一樣停在 401 | 中高 | 同上 |
| E2-3 | code-review 是 **failure**。只有 trivy 那個 job 失敗，static 和 codeql job 都 success | 中 | `trivy-action` 是 composite，裡面的 `aquasecurity/setup-trivy` 不在清單上（`actions/cache` 屬於 GitHub 官方，會放行） |
| E2-4 | trivy job 的原因**看得到**，在 job log 裡點名 `aquasecurity/setup-trivy` | 中 | 巢狀的 composite 要到 runner 下載時才解析得到，所以是 job 層級的失敗，會有 log |

## E3：`all` + `sha_pinning_required=true`

| # | 預期 | 信心 | 依據 |
|---|---|---|---|
| E3-1 | collect **不是** success（U2 = 強制釘 SHA 會套到 kit 內部的 tag 引用） | 中高 | 反過來想：如果不套用，只要包一層 reusable workflow 就能繞過這個政策 |
| E3-2 | 被點名的是 kit 內部的 `actions/*@vN`，**不是** `@v1` 那個 reusable workflow | 高 | 文件明寫「reusable workflow 仍然可以用 tag 引用」 |
| E3-3 | code-review、post 和 collect 一樣；conclusion 和 E1 同型 | 中 | 同一套檢查機制 |

## 對照：還原後再跑一次

| # | 預期 | 信心 |
|---|---|---|
| C-1 | GET 回來的 JSON 跟實測前一模一樣 | 高 |
| C-2 | collect success、code-review success、post 停在 401，跟 09-23 一樣 | 高 |

## 判讀規則（先寫死）

- 「被擋」：conclusion ≠ 基準。只要原因文字點名了 action，就以原因為準。
- 預期寫「不是 X」，結果只要不是 X 就算命中；預期寫「是 X」，結果要正好是 X 才算命中。
- 信心欄不回頭改。命中率只拿來回頭看自己的判斷準不準，不當成結論。

## 追加 E2b（2026-09-24 12:21 UTC 登記，在觸發之前）

起因：寫 USAGE 時發現，加上 `aquasecurity/setup-trivy@*` 的那份完整清單**沒有實測過**。E2 只驗到「少了它 Trivy 會失敗」。
靜態查過 `setup-trivy@3fb12ec` 的 `action.yaml`：它是 composite，裡面引用 `actions/cache/restore`、`actions/checkout`、`actions/cache/save`，三個都是 GitHub 官方的，也都釘了 SHA。

設定：E2 + `aquasecurity/setup-trivy@*`

| # | 預期 | 信心 |
|---|---|---|
| E2b-1 | collect success | 高 |
| E2b-2 | post 停在 401 | 高 |
| E2b-3 | code-review **success**：reviewdog、gitleaks、Analyze、Trivy 四個 job 都 success，dependency review skipped | 中高（前提是 setup-trivy 裡沒有更深一層的第三方引用；靜態看是沒有） |
