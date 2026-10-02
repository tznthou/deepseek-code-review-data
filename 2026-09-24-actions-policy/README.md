# 2026-09-24 caller 的 Actions 政策會不會擋住 kit（probe 實測）

> 狀態：**已結案**。
> - 實測：2026-09-24 12:10–12:23 UTC，$0。probe 的設定已經還原，也跑過對照組確認。
> - 文件：PR #34 由子超確認後 squash merge（`daf9b78`，12:29:16 UTC，`--match-head-commit 2de13e2`），merge 後的 tree 跟 PR head 一致。
> - 子超 2026-09-24 裁定「改 kit 釘 SHA」：跟 concurrency 修正、內插一致性併成同一版，放下一輪。發版後重跑 E3 當回歸測試。
> 來源：09-24 在另一個專案（private repo）做導入驗收時，驗收 AI 指出 USAGE 缺一個坑：「repo 的 Actions 政策如果只允許本 repo 的 actions，第一次跑就會 startup_failure」。這點一直沒有實測。
> 範圍擴大：09-24 盤點時發現 `actions/permissions` API 多了 `sha_pinning_required` 欄位，所以把「強制釘 SHA」也一起測。

## v1.4.1 要做的四項（2026-09-25 從 code 核對；位置標那一行的內容，不寫行號）

RESUME 原本說這四項的細節與行號都在本檔，實際上本檔只有 ① 的表格，③④ 只存在 RESUME 的一行。
09-25 從 code 重新核對後補在這裡。**③④ 的原始理由沒有留下紀錄**（本目錄、PR #33–#37 的 review、
ccRecall 都查過），下面的「為什麼」是從 code 推的，不是當初的原話。

1. **19 處 `uses:` 改完整 SHA + `# vN` 註解**：清單見下面「kit 用到的 action」那張表。09-25 核對：仍是 19 處、0 處釘 SHA
   - ⚠️ **09-26 更正（實作計畫在 `../2026-09-26-v1.4.1/README.md`）**：註解要寫完整的 `# vX.Y.Z` 並放在行尾，`# vN` 會讓 Dependabot 不更新註解（dependabot-core PR #5951）；`dependency-review-action` 的 `v5` 是 branch 不是 tag；本 repo 的 01/02/05/eval-filter 另有 18 處沒算進 19
2. **新增 `.github/dependabot.yml`**：09-25 仍不存在。釘 SHA 之後，要靠它開 PR 提醒升級
3. **`reusable-ai-review-post.yml` 的 concurrency group 加 `head_repository`**：現在是
   `ai-review-post-${{ github.event.workflow_run.head_branch }}` 加 `cancel-in-progress: true`。
   推論：兩個 fork 的 PR 如果 branch 同名（`main`、`patch-1` 這類），會落在同一個 group，
   後到的 run 取消先到的，先到的 PR 就拿不到 review → group 連 `github.event.workflow_run.head_repository.full_name` 一起放
4. **`run:` 裡直接內插 caller input 的 6 處改走 `env:`**：`reusable-ai-review-post.yml` 的
   `--min-severity`、`--min-confidence`、`--max-inline`；`reusable-static-review.yml` 的 `-efm=`、`-name=`、`-fail-level=`。
   同一支檔案的其他 input（`LINT_COMMAND`、`CUSTOM`、`DEEPSEEK_MODEL`…）已經走 env。
   值由 caller 自己的 workflow 檔決定，不是外部 PR 作者控制的，所以是一致性問題不是注入漏洞；
   但 `'${{ }}'` 先展開才交給 shell，值裡有單引號就會提前結束引號 → [[actions-expression-boundary]]

## 下一輪重跑 E3 用的腳本（`scripts/`）

v1.4.1（原訂 v1.3.2）把 kit 內部的 action 釘成 SHA 之後，要重跑 E3 當回歸測試。這幾支腳本就是為這件事留的：

- `commit.py <label> <msg檔>`：在 probe 的 `trigger` 分支改 `app.py` 建一個 commit，印出新 SHA。要在 `scripts/` 目錄裡跑，因為訊息檔用相對路徑
- `poll.sh <T0> [秒]`：等 T0 之後建立的 collect／code-review 跑完，再最多等 120 秒看 post
- `inspect.sh <run_id>`：原因分別在哪裡看得到（`gh run view`、`--log-failed`、jobs、check-runs）
- `ann2.py <owner/repo> <run_id>`：抓 public run 頁面的 Annotations
- `msg-e3.txt`：E3 的 commit 訊息，重跑時改寫成「驗 v1.4.1」

照 README 前面的還原指令收尾。每一組都要先寫預期再觸發。

## ⚠️ 還原（session 中斷時照這裡做）

probe 在實測前的設定（2026-09-24 12:0x UTC 用 GET 查的）：

```
{"enabled":true,"allowed_actions":"all","sha_pinning_required":false}
```

`selected-actions` 在 `all` 模式下 GET 會回 409（"All actions and workflows are allowed"），所以沒有既有的清單要保留。

還原指令：

```
gh api -X PUT repos/tznthou/deepseek-review-probe/actions/permissions -F enabled=true -f allowed_actions=all -F sha_pinning_required=false
gh api repos/tznthou/deepseek-review-probe/actions/permissions   # 要跟上面那行 JSON 完全一樣
```

## 文件查到的事實（docs.github.com 的 article API，2026-09-24 抓的全文）

- 「只允許 OWNER 的 actions」會擋掉所有 GitHub 官方的 action，文件舉的例子就是 `actions/checkout`。
  出處：repositories/…/managing-github-actions-settings-for-a-repository，"Managing GitHub Actions permissions" 第 4 步。
- 「強制釘 SHA」：所有 action 都要釘到完整的 commit SHA，包括 OWNER 自己的和 GitHub 官方的；**reusable workflow 仍然可以用 tag 引用**。repo 和 org 兩層都有這個設定。
  出處：同一頁，以及 organizations/…/disabling-or-limiting-github-actions-for-your-organization、actions/reference/security/secure-use。
- 允許清單裡寫 reusable workflow 的語法是 `OWNER/REPOSITORY/PATH/FILENAME@TAG-OR-SHA`，可以用 `*` 萬用字元。
- caller repo 的 Actions permissions 必須允許使用 reusable workflow。
  出處：actions/reference/workflows-and-actions/reusing-workflow-configurations，"Access to reusable workflows"。

**文件沒寫、要靠實測的**：

- U1：caller 的政策，會不會套用到「別的 repo 的 reusable workflow **裡面**用到的 action」？
- U2：強制釘 SHA，會不會套用到 kit 內部的 `actions/checkout@v7` 這類 tag 引用？如果會，caller 自己不管怎麼釘都跑不起來，要改的就是 kit。
- U3：被擋的時候，run 的 conclusion 是 `startup_failure` 還是 `failure`？原因從哪裡看得到？
- U4：個人帳號的 repo 設「只允許 OWNER」時，OWNER 是否涵蓋同一個帳號的其他 repo？
  - 涵蓋的話：probe（tznthou）引用 kit（tznthou）不會被擋，但也因此**測不到外部使用者要加的 kit pattern**。
  - 不涵蓋的話：可以測。

## kit 用到的 action（`uses:` 共 19 處，全部用 tag 引用）

| reusable | 用到的 action |
|---|---|
| ai-review-collect | `actions/checkout@v7`、`actions/upload-artifact@v7` |
| ai-review-post | `actions/checkout@v7` ×2、`actions/download-artifact@v8`、`actions/upload-artifact@v7` |
| static-review | `actions/checkout@v7` ×3、`reviewdog/action-setup@v1`（composite，裡面沒有再引用）、`gitleaks/gitleaks-action@v3`（node24）、`actions/dependency-review-action@v5`（node24） |
| codeql | `actions/checkout@v7` ×3、`github/codeql-action/{init,analyze,upload-sarif}@v4`、`aquasecurity/trivy-action@v0.36.0` |

`trivy-action@v0.36.0` 是 composite，裡面還引用 `aquasecurity/setup-trivy@3fb12ec…`（v0.2.6）和 `actions/cache@27d5ce7…`（v5.0.5），**這兩個都釘了 SHA**。

## 計畫

每一組的順序：改設定 → GET 確認 → push commit 到 `trigger` → 等 collect／code-review／post 全部跑完 → 記錄 → 才換下一組（post 是 `workflow_run` 觸發，開始時才判定政策，不能在它跑之前換設定）。

- E1：`allowed_actions=local_only`
- E2：`allowed_actions=selected` + `github_owned_allowed=true`、`verified_allowed=false`、`patterns_allowed=["reviewdog/action-setup@*","gitleaks/gitleaks-action@*","aquasecurity/trivy-action@*"]`
  - 這是「照 kit 的 `uses:` 清單去開允許清單」的補救設定。要驗證這樣夠不夠，也看會不會冒出沒列到的巢狀 action。
  - **先登記的分支**：如果 E1 顯示 kit 本身被擋（U4 = 不涵蓋），E2 的 patterns 就再加一條 `tznthou/deepseek-code-review/.github/workflows/*@*`。
- E3：`allowed_actions=all` + `sha_pinning_required=true`
- 還原後再跑一次當對照組，確認 probe 回到可以做回歸的狀態（結果應該和 09-23 那次一樣）。

每一組要記的：三支 workflow 的 conclusion、job 清單、原因分別在 `gh run view`、`--log-failed`、check-run annotations 看不看得到、被點名的是哪個 action。

成本：假 key，$0。probe 是 public，不花 Actions 分鐘數。

## 結果

### E1：`local_only`（trigger commit `f1f157b`，12:10:30 UTC）

- collect `35997408363`：**`startup_failure`**，0 秒，0 個 job，check suite 裡 0 個 check-run
- code-review `35997407414`：**`startup_failure`**，0 秒
- post：**沒有被觸發**。collect 跑完後等了 120 秒，一直沒有出現
- 原因在哪裡看得到：
  - `gh run view`：只有「X This run likely failed because of a workflow file issue.」
  - `--log-failed`：`failed to get run log: log not found`
  - jobs、check-run annotations：都是空的
  - **只有網頁的 run 頁面看得到**（Annotations 1 error；public repo 不用登入，用 curl 抓 HTML 就拿得到）：
    - collect：`The actions actions/checkout@v7 and actions/upload-artifact@v7 are not allowed in tznthou/deepseek-review-probe because all actions must be from a repository owned by tznthou.`
    - code-review：`The actions actions/checkout@v7, reviewdog/action-setup@v1, gitleaks/gitleaks-action@v3, actions/dependency-review-action@v5, github/codeql-action/init@v4, and 3 others are not allowed …`
  - **`actions/dependency-review-action@v5` 也被點名了**：probe 傳了 `skip-dependency-review: true`，那個 job 根本不會跑。所以檢查是在解析階段掃過所有 `uses:`，不看 `if:`
- U1 = **會套用**：caller 的政策會檢查別的 repo 的 reusable workflow 裡面用到的 action
- U4 = **涵蓋**：kit 的 reusable workflow 沒被點名，個人帳號的 OWNER 涵蓋同一個帳號的其他 repo。所以 probe **測不到外部使用者要加的 kit pattern**

預期對照：E1-1 ✅、E1-2 ✅、E1-3 ✅、E1-4 ✅、**E1-5 ❌**（post 根本沒被觸發）、E1-6 ✅

### 順帶查到：另外兩種 startup_failure 的原因，網頁上也看得到

回頭抓了兩個 repo 裡留下來的 startup_failure run 頁面：

| run | 原因（Annotations 原文節錄） |
|---|---|
| probe `35521125655`（09-20，漏 permissions，也就是 memory 的 Q4） | `Invalid workflow file … The nested job 'review' is requesting 'actions: read, pull-requests: write', but is only allowed 'actions: none, pull-requests: none'.` |
| kit `35690636479`（09-22，發版前兩分鐘的破窗） | `Invalid workflow file … Invalid secret, REVIEW_BLOCKED_TERMS is not defined in the referenced workflow.` |
| kit `35574114706`（09-21，`v1.2.0` 拿掉 input） | `Invalid workflow file … Invalid input, filter-findings is not defined in the referenced workflow.` |

⇒ memory Q4 和 USAGE 第 4 點說「三種工具都驗不出來」只對了一半：CLI 確實看不到，但**網頁的 Annotations 一直都寫著原因**。政策擋下的訊息開頭沒有 `Invalid workflow file`，跟另外三種不一樣。

### E2：`selected` + GitHub 官方 + 三條 pattern（trigger commit `2b0ead1`，12:13:23 UTC）

設定用 GET 確認過：`{"github_owned_allowed":true,"patterns_allowed":["reviewdog/action-setup@*","gitleaks/gitleaks-action@*","aquasecurity/trivy-action@*"],"verified_allowed":false}`

- collect `35997709971`：**success**（11 秒）
- post `35997734118`：failure，**停在 HTTP 401**，跟基準一樣。log 有 `@refs/tags/v1 (cffcc42…)` → `HEAD is now at ff63650`，filter-findings no-op 的 `##[warning]` 也還在
- code-review `35997710114`：**failure**（44 秒）。5 個 job 當中：
  - reviewdog、gitleaks、CodeQL Analyze 三個 success
  - dependency review 是 skipped（probe 刻意跳過的）
  - **只有 Trivy 失敗**：`##[error]The action aquasecurity/setup-trivy@3fb12ec12f41e471780db15c232d5dd185dcb514 is not allowed in tznthou/deepseek-review-probe because all actions must be from a repository owned by tznthou, created by GitHub, or match one of the patterns: aquasecurity/trivy-action@*, gitleaks/gitleaks-action@*, reviewdog/action-setup@*.`
  - 這個原因在 `--log-failed` 和網頁都看得到。巢狀 composite 被擋是**執行階段的 job 失敗**，不是 startup_failure
- ⇒ 要讓 kit 完整跑起來，允許清單要有：
  - GitHub 官方的 action
  - `reviewdog/action-setup`、`gitleaks/gitleaks-action`、`aquasecurity/trivy-action`
  - **`aquasecurity/setup-trivy`**，照 kit 的 `uses:` 清單去開會漏掉這一條
  - 外部使用者還要加 kit 本身的 pattern（這一條測不到，見 U4）
  - 只裝 AI review 那兩支的話，GitHub 官方的 action 就夠了

預期對照：E2-1 ✅、E2-2 ✅、E2-3 ✅、E2-4 ✅

### E3：`all` + `sha_pinning_required=true`（trigger commit `b49cb57`，12:14:55 UTC）

- collect `35997863716`：**`failure`**（6 秒，**不是 startup_failure**）。job 只有 Set up 一步，原因在 log 裡：
  `##[error]The actions actions/checkout@v7 and actions/upload-artifact@v7 are not allowed in tznthou/deepseek-review-probe because all actions must be pinned to a full-length commit SHA.`
- code-review `35997863718`：**`failure`**（9 秒）。有跑的 4 個 job 全部在 Set up 階段失敗，點名的都是 kit 內部的 tag 引用：
  - `checkout@v7`
  - `codeql-action/init@v4`、`codeql-action/upload-sarif@v4`
  - `reviewdog/action-setup@v1`
  - `gitleaks-action@v3`
  - `trivy-action@v0.36.0`
  - dependency review 是 skipped，**沒有被點名**。E1 在解析階段就把它點名了，這裡差別在於：這個檢查是在 job 執行階段做的
- post `35997878890`：**`skipped`**。有被 `workflow_run` 觸發，但 kit 的 post job 有 `if: workflow_run.conclusion == 'success'`（`reusable-ai-review-post.yml:104-106`），collect 失敗所以跳過
- caller 引用的 `@v1` 沒有被點名，符合文件寫的「reusable workflow 仍然可以用 tag 引用」
- U2 = **會套用**。開了強制釘 SHA 的 caller，**不管自己怎麼釘 kit，都跑不起來**，因為被擋的是 kit 裡面的 19 處 tag 引用。要支援這類 caller，只能改 kit
- U3 補充：政策被擋有兩種機制
  - `local_only` 在建立 run 時就判定 → startup_failure，原因只有網頁上看得到
  - 強制釘 SHA 在 job 的 Set up 階段判定 → failure，`--log-failed` 就看得到原因
  - 巢狀 composite 被擋（E2）也屬於後者

預期對照：E3-1 ✅、E3-2 ✅、**E3-3 ❌**（conclusion 是 failure，不是 startup_failure；post 是 skipped，不是被擋）

### 對照：還原後（trigger commit `1d78def`，12:16:08 UTC）

- C-1 ✅：GET 回來的是 `{"enabled":true,"allowed_actions":"all","sha_pinning_required":false}`，用字串比對過，跟實測前一模一樣
- C-2 ✅：
  - collect `35997994822` success
  - code-review `35997994835` success
  - post `35998016794` 停在 HTTP 401，`@refs/tags/v1 (cffcc42…)` → `HEAD is now at ff63650`，filter-findings 的 `##[warning]` 也在
  - 結果跟 09-23 那次一樣，probe 回到可以做回歸的狀態

### E2b：E2 + `aquasecurity/setup-trivy@*`（trigger commit `423bb71`，12:22:01 UTC）

補跑的原因：寫 USAGE 時才發現，加上 setup-trivy 的完整清單沒有實測過（預期在觸發前追加登記在 `expectations.md`）。

- collect `35998603719` success
- post `35998625163` 停在 401（`@refs/tags/v1 (cffcc42…)` → `ff63650`）
- code-review `35998603623` **success**：Trivy、gitleaks、reviewdog、Analyze 四個都 success，dependency review 是 skipped
- 12:23:29 UTC 還原，GET 用字串比對過，跟實測前一模一樣。這次沒有再跑對照組：唯一的變數是設定，第一次還原後的對照組已經證明 `all` 可以正常跑

預期對照：E2b-1 ✅、E2b-2 ✅、E2b-3 ✅

## 結論

**命中 16/18**（原本 15 條中 13，加上追加的 E2b 3/3）。沒猜中的兩條（E1-5、E3-3）錯在同一個假設：我以為政策只有一種判定機制，實際上有兩種，而且後續影響不同：

| | `local_only` 擋最外層 | 強制釘 SHA／巢狀 composite |
|---|---|---|
| 判定時間點 | 建立 run 時 | job 的 Set up（或執行到那一步時） |
| conclusion | `startup_failure`，0 個 job | `failure` |
| CLI 看得到原因嗎 | ❌ 只說 "workflow file issue" | ✅ `--log-failed` 有 `##[error]` |
| 有沒有觸發 post | ❌ 不會觸發 | 會觸發，但被 kit 的 `if:` 跳過（skipped） |
| `if:` 不會執行的 job | 一樣會被點名 | 不會被點名 |

要寫進 USAGE 的事：

1. **驗收 AI 說的坑是真的**，而且比它說的更具體：
   - 範圍是整組，不只是第一次跑：連只要 `contents: read` 的 collect 也會掛掉
   - 原因只有網頁上看得到
2. **`selected` 模式要允許的清單**：
   - 只裝 AI review 兩支：GitHub 官方的 action 就夠了
   - code-review.yml：再加 4 條，其中 `aquasecurity/setup-trivy` 照 `uses:` 抄一定會漏
   - 外部使用者還要加 kit 的 pattern，這條**沒辦法實測**（U4）
3. **強制釘 SHA 的 caller 目前完全不能用這套**。要支援只能改 kit，caller 自己怎麼釘都沒用
4. **第 4 點（漏 permissions）的診斷要改寫**：原因寫在網頁的 Annotations（三個歷史 run 都驗過），不是「查不出來」。另外可以用「連 collect 都掛 → 先查政策；只有需要 write 的掛 → 查 permissions」來區分

如果要改 kit（待子超決定）：

- 靜態查過，kit 用到的 GitHub 官方 action 都是 node24，裡面沒有再引用別的 action
- `reviewdog/action-setup` 是 composite，但裡面沒有引用
- `trivy-action` 裡的兩個巢狀引用本來就釘了 SHA
- ⇒ **把 kit 那 19 處引用改成完整 SHA，理論上就夠了**
- 驗證方式：發版後重跑 E3，這就是現成的回歸測試

### 過程中自己踩的坑

- 查第三方 action 時用 `set -- $spec` 拆參數，被 zsh 不斷字的行為擋下。這就是 RESUME 記過的 shell 坑①
- 查巢狀引用的函式用了 `local … path=…`，而 **zsh 的 `path` 是跟 `$PATH` 綁在一起的陣列**。結果 `gh` 從 PATH 消失，6 個查詢全部回「not found」。因為那個函式把錯誤導進了 `/dev/null`，**看起來就像「查無資料」**，換變數名重跑才發現
- 兩次在主 session 裡 `cd` 進 scratchpad，harness 的工作目錄就被換走了。這是 RESUME 記過的 harness 事實⑤

## 附錄：v1.4.1 回歸要順便測的 Dependabot（2026-09-24 查證，2026-09-25 從 RESUME 下沉）

- **Dependabot 不擋「新增 `.github/dependabot.yml`」那一步**：本 repo 四種 Dependabot 開關全關，kit／probe／另一個專案（private repo）都是 0 個 Dependabot PR（claude-prism 正向對照有 6 個）
- 文件寫的：Dependabot 觸發的 push／pull_request 拿不到 Actions secret，所以 `03` 不受影響（它本來就零 secret）
- 文件**沒寫**的：`04` 走 `workflow_run` 間接觸發，拿不拿得到 secret 不知道。拿得到 = 每個 PR < $0.01；拿不到 = 失敗一筆、$0
- `USAGE.md` 的「**bot 開的 PR 一樣會觸發。**」那一條寫 Dependabot 開的 PR 也會送去 review，這句沒實測過（09-24 記的是 `:469`，被 PR #37 推到 `:483`，改標內容）
- **測法**：v1.4.1 回歸時，在 probe 放一份 `dependabot.yml` 加一個刻意用舊版的 pin。用假 key 就分得出三種結果：401 = 拿到 secret；「缺少 DEEPSEEK_API_KEY」= 拿到空值；startup_failure = 被 `required: true` 卡住
