# 2026-09-26 v1.4.1：kit 內部 action 釘 SHA + 兩個 reusable 小修

> 狀態：**`v1.4.1` 已發版（2026-09-26 11:42:51 UTC 移 `v1`），probe 三段 24/24；D8 文件 PR #42 已 merge（`37d4aa4`，11:51:57 UTC，子超核可），post 的 ④ 實跑通過**。剩 D9（第一個 Dependabot PR，被動觀察）。範圍子超 09-26 定 C（37 處）＋ 加 [18]。進度見文末，probe 結果見 `expectations.md`。
> 上游 SSOT：`../2026-09-24-actions-policy/README.md` 開頭「v1.4.1 要做的四項」。本檔是實作計畫與之後的進度記錄。
> 裁定：子超 09-24「改 kit 釘 SHA，跟 concurrency 修正、內插一致性併成同一版」；09-26「同意先做 v1.4.1」。

## 目標

讓開了「強制 action 釘 SHA」（`sha_pinning_required=true`）的 caller 能用引用路線。
09-24 E3 實測：被擋的是 kit 裡面的 tag 引用，caller 自己怎麼釘都沒用 → 只能改 kit。

## 09-26 盤點（對 code 與 GitHub 重驗，不照抄 SSOT）

- reusable 內部 `uses:` 仍是 **19 處**、0 處釘 SHA（collect 2、post 4、static 6、codeql 7）
- **SSOT 沒算到的**：本 repo 自己的 workflow 另有 **18 處** tag 引用
  - `01-static-review.yml` 6 處、`02-codeql.yml` 6 處：同時是 dogfood 與**複製路線的範本**（README §2 步驟 1、SETUP-CHECKLIST）；01/02 是獨立 workflow，不呼叫 reusable
  - `05-dsh-agent-review.yml` 4 處（評估紀錄，job 平常是 skipped）、`eval-filter.yml` 2 處（手動觸發）
- ③ concurrency：`reusable-ai-review-post.yml` 仍是 `ai-review-post-${{ github.event.workflow_run.head_branch }}`
- ④ 6 處內插仍在：post 的「貼回 PR」step 3 處、static 的「Post findings on changed lines only」step 3 處，全部是 `'${{ inputs.x }}'` 單引號包住
- `.github/dependabot.yml` 不存在；repo 沒有 requirements／pyproject／package.json（腳本只用標準函式庫）→ 只需要 github-actions 這個 ecosystem
- selftest 只有 [17] 讀 workflow（`input_default` 讀 input 區塊的 `default:`），改 ④ 碰不到
- 02 在 PR 上會實跑兩個 job 的全部 action（run `36106149940`：Analyze = checkout／init／analyze，Trivy = checkout／Run Trivy／upload-sarif）

### SSOT 要更正的兩件事（已在上游 SSOT 標註）

1. **註解格式不能寫 `# vN`**。Dependabot 更新 SHA 時，是在註解裡找「舊的完整版本字串」換成新的（dependabot-core PR #5951）：
   - 只寫 major（`# v7`）找不到 `7.0.1` → 註解不會更新，SHA 換了註解還停在原地
   - 版本號後面還有字（`# v0.36.0 ⚠️ …`）→ 刻意跳過（怕改到說明文字）
   - ⇒ 一律 `# vX.Y.Z`，而且放在行尾。`reusable-codeql.yml` trivy 那行的 `# ⚠️ tag 有 v 前綴` 要拿掉
2. **`actions/dependency-review-action@v5` 的 `v5` 是 branch 不是 tag**（`refs/heads/v5`；tag 只有 `v5.0.0`，兩者同一個 commit）

### Dependabot 會不會自動把 tag 轉成 SHA

不會。dependabot-core PR #16029（2026-08-27 merge）做了這個功能，但藏在 feature flag 後面，還沒開放設定。所以沒釘的 `uses:` 會維持 tag 引用。

## 要釘的 SHA（2026-09-26 `git ls-remote` 解析，annotated tag 取 `^{}`）

| action | 現在 | commit SHA | 註解 |
|---|---|---|---|
| `actions/checkout` | `@v7` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `# v7.0.1` |
| `actions/upload-artifact` | `@v7` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | `# v7.0.1` |
| `actions/download-artifact` | `@v8` | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | `# v8.0.1` |
| `actions/dependency-review-action` | `@v5`（branch） | `a1d282b36b6f3519aa1f3fc636f609c47dddb294` | `# v5.0.0` |
| `actions/setup-node`（只有 05） | `@v7` | `820762786026740c76f36085b0efc47a31fe5020` | `# v7.0.0` |
| `actions/cache`（只有 05） | `@v6` | `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` | `# v6.1.0` |
| `github/codeql-action/{init,analyze,upload-sarif}` | `@v4` | `2892aa5e19bbd11bc0cff5427e3b750a04d9e3c2` | `# v4.38.2` |
| `aquasecurity/trivy-action` | `@v0.36.0` | `ed142fd0673e97e23eac54620cfb913e5ce36c25` | `# v0.36.0` |
| `reviewdog/action-setup` | `@v1` | `d8a7baabd7f3e8544ee4dbde3ee41d0011c3a93f` | `# v1.5.0` |
| `gitleaks/gitleaks-action` | `@v3` | `e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e` | `# v3.0.0` |

釘的是「現在 tag 指向的那個 commit」→ **action 本身的 code 不變**。action 執行時才下載的東西（`reviewdog_version: latest` 的 binary、trivy DB、CodeQL bundle）本來就不受 SHA 控制，釘了也一樣會變——CHANGELOG 不能寫成「供應鏈鎖定」。

**D3 已完成（2026-09-26，`scratchpad/check_pins.py` 同內容）**：10 個 SHA 用 `gh api repos/{repo}/git/commits/{sha}` 驗過都是 commit；各版本的 action.yml：官方 action 全部 `node24`、沒有巢狀引用；`trivy-action` 是 composite，巢狀引用 `setup-trivy@3fb12ec…`、`cache@27d5ce7…` 本來就釘了 SHA；`reviewdog/action-setup` 是 composite 但裡面沒有 `uses:`；`gitleaks-action` 是 `node24`。⇒ 09-24「把 19 處改成 SHA 理論上就夠」的前提，在這次要釘的版本上仍成立。

## 範圍（待子超決定）

- **A**：只釘 reusable 內部 19 處（SSOT 原範圍）
- **B**：A + 01/02 的 12 處 = 31 處
- **C**：B + 05 的 4 處 + eval-filter 的 2 處 = 37 處

建議 C。理由：

1. **這是發版前唯一能實跑 SHA 的方法（B 就有）**。改 reusable 的 PR 上，03/04 跑的是 `@v1`（已發布舊版）→ reusable 的新 SHA 一行都不會執行（[[dogfood-only-bugs]]）。01/02 是本 repo 直接跑的 workflow，釘同一組 SHA 後，PR CI 全綠 = checkout／reviewdog／gitleaks／dependency-review／codeql ×3／trivy 的 SHA 都實跑過。發版前沒實跑到的只剩 upload/download-artifact
2. 日後 Dependabot 的 grouped PR 會同時改 01/02 與 reusable 的同一個 action → 那個 PR 的 CI 一樣有實跑驗證（B 就有；待 D9 確認 Dependabot 真的會一起改）
3. 複製路線的使用者直接拿到釘好的範本（B 就有）
4. **B 和 C 只差 05/eval-filter 這 6 處**：換來 Dependabot 行為一致（全部是 SHA 更新，不會有幾支只在出新 major 時才動）、沒有例外清單。05 是評估紀錄、eval-filter 手動觸發，兩者都沒有使用者受益

## 改動清單

PR α（`chore/pin-actions-sha`，主體；一個 PR，因為 ①③④ 改的是同一批檔案，拆開會衝突。CHANGELOG 分條、PR body 分節）：

1. 範圍內的 `uses:` 改成 `@<40 字元 SHA> # vX.Y.Z`（用腳本替換，替換後再用腳本比對上表）
2. 新增 `.github/dependabot.yml`：`github-actions`、`directory: /`、weekly、所有更新 group 成一個 PR（10 個 action 分開開會有 10 個 PR，每個都觸發 AI review）
3. `reusable-ai-review-post.yml` concurrency group 加 `github.event.workflow_run.head_repository.full_name`。萬一這個欄位取不到，expression 得到空字串，group 退回只用 branch＝現在的行為，不會壞
4. 6 處 caller input 改走 step 的 `env:`，run 裡用 `"$VAR"`
5. selftest 新增 [18]（見下；**自己加的，不在裁定內**）
6. CHANGELOG `[Unreleased]`：Changed（釘 SHA、Dependabot、**代價：action 的修正版要等 kit 發版才到 `@v1` 的 caller**）＋ Fixed（concurrency、內插）
7. README 樹狀圖加 `dependabot.yml`；[18] 若採用，selftest 組數／項數同步散落 4 處（README badge／樹狀圖註解／§8／SETUP-CHECKLIST §9 括號）

PR β（`docs/post-review-docstring`，已有 commit `6845779`）：補一條 CHANGELOG 後 push。跟 α 性質不同（docs vs 行為），分開 review。

之後：PR γ 發版 `chore: 發布 v1.4.1`；PR δ 文件改寫（驗證通過後才改）。

### selftest [18]：workflow 的供應鏈與內插（自己加的）

為什麼要：v1.4.1 的承諾（強制釘 SHA 的 caller 能用）壞掉時，**本 repo 所有 CI 仍是全綠**——本 repo 沒開 `sha_pinning_required`，03/04 又跑 `@v1`。日後有人（包括 AI）順手加一個 `@v4` 就會靜默破壞。actionlint 補不到：它會抓 untrusted 的 `github.event.*` 內插，但把 `inputs.*` 當 trusted、也不檢查釘 SHA。
代價：selftest 組數／項數散 4 處要同步（#21/#22/#27 都漏過）。

4 項：

1. 找得到外部 action 的 `uses:`（防 regex 寫錯 → 空集合 → 全部 PASS）
2. 外部 action 全部是 `@<40 hex> # vX.Y.Z`，版本號在行尾（排除註解行、`./` 本地引用、`/.github/workflows/` 的 reusable 引用）
3. reusable 的 `run:` 區塊（含單行 `run:`）裡沒有 `${{ inputs.`
4. 探針（合成文字）：`run:` 裡的內插要抓到、`env:`／`with:` 的值不算——run 區塊用縮排界定，是四項裡最脆弱的解析

red-green：[18] 在 main 上 2／3 要 FAIL、1／4 要 PASS；改完全部 PASS。用 `git checkout HEAD -- <workflow 檔>` 還原被修的檔案、保留新測試（不用 stash，[[red-green-probes-pass-both-versions]]）。

## Done（可檢查）

- D1 selftest 全綠；[18] 的 red-green 照上面
- D2 actionlint 十支 workflow 乾淨
- ~~D3~~ 已完成（見上）；動工時再跑一次 `git ls-remote` 確認 tag 沒移動（移動了也不影響正確性，只影響註解是不是最新）
- D4 PR α 上 01/02 全綠（範圍 B/C 時才有這條）
- D5 發版（**兩段式，見下**）
- D6 probe 回歸（跑前寫預期表）：collect success、code-review success、post 停在 401，跟 v1.4.0 一樣 → upload/download-artifact 的 SHA 在這一步才實跑
- D7 重跑 E3：probe 設 `sha_pinning_required=true` → collect success、code-review success（dependency review skipped）、post 停在 401 → 還原後 GET 字串比對
- D8 PR δ：USAGE「第 2 步」最後一節與 `:35`／`:195`／`:206` 表格、README §7 故障排除那列、（B/C）USAGE 複製路線那句
- D9（**不擋發版**）第一個 Dependabot PR：有改到 `reusable-*.yml`、01/02 與 reusable 的同一個 action 註解一致（#7376）、03/04 的 `reusable-*.yml@v1` 沒被動到。同一個 PR 會走本 repo 的 03→04（真 key），結果直接回答 SSOT 附錄「`04` 拿不拿得到 secret」——附錄那個在 probe「刻意用舊版 pin」的測法不必做
  - ⚠️ **2026-09-30 查: Dependabot 09-28 (週一) 沒跑**. `dependabot.yml` 是 `interval: weekly`、沒寫 `day`; 官方文件 (options reference) 原文 "Use `weekly` to run once a week, by default on Monday", 時間隨機. 但 Actions 裡 event=dynamic 的 run 總共 2 筆 (= 09-26 11:30 UTC 建檔那兩次), 09-27 之後 134 筆 run 分頁查完 0 筆「Dependabot Updates」. 原因沒查. **10-05 (週一) 後再查一次, 仍沒跑就改成待查問題, 不再當被動等**; 網頁交叉確認點: Insights → Dependency graph → Dependabot 的 Last checked

### D5 兩段式發版（計畫審查第一輪可逆性 FAIL 的修法）

`v1` 一移動就推到所有 `@v1` 的 caller（另一個專案（private repo）、probe、本 repo 03/04），而 upload/download-artifact 的 SHA 在那之前沒實跑過。所以驗證要放在移 `v1` 之前：

1. 發版 PR γ merge → 在 merge commit 打 annotated tag `v1.4.1`，push tag；**不建 Release、不移 `v1`**
2. D6 前先確認 probe 狀態：Actions 政策 GET = 還原後那行 JSON、`trigger` 分支與 PR #1 仍在
3. probe **main** 上的三支 caller 改釘 `@v1.4.1`，有 `kit-ref` 的一起改成 `v1.4.1`（[[floating-major-tag-contract]]）。post 是 `workflow_run` 觸發，跑的是 probe main 的 caller，改 trigger 分支沒用
4. D6 → D7（E3 設定改動與還原照上游 SSOT「還原」段）
5. probe 三支 caller 改回 `@v1`／原本的 `kit-ref`（**這步是 Done 條件**：忘了改回，之後的回歸測的就不是 `v1`）
6. 建 `v1.4.1` Release（Latest）、`git tag -f v1 v1.4.1`、push `v1` 帶 `-f`
7. 再觸發一次 probe，確認 `@v1` 這條路（expect 同 D6）

失敗時：v1.4.1 有問題就修好發 v1.4.2，`v1` 從頭到尾沒動、沒有 caller 受影響；`v1.4.1` tag 留著但不建 Release。

## 對外動作的確認點

- push branch、開 PR：直接做（可關閉）
- 每個 PR 的 merge、打 tag、改 probe 的 caller 與 Actions 設定、建 Release 與移 `v1`：先問子超（D5 可以在第 1 步前一次確認整段）

## 明確不做

- Dependabot `cooldown`、Dependabot security updates（repo 設定，不受 schedule 限制；要不要開另議）
- `github.repository`、`head_sha`、`steps.pr.outputs.number` 的內插：值由 GitHub 產生、格式固定，不是 caller input
- 01/02 與 reusable 兩份實作的分岔（[[dual-entry-config-drift]] 的同型，另案）
- 本 repo 開 `sha_pinning_required`（要發版後才能開，而且對 reusable 內部沒有保護力：PR 上跑的是 `@v1`）
- 引入 pinact／zizmor：一次性替換寫小腳本、之後交給 Dependabot；檢查放 selftest，不加新依賴
- SSOT 附錄的 probe Dependabot 測法（被 D9 取代）

## 風險與退路

- SHA 錯 → 解析 action 時失敗。緩解：D3（已過）＋ D4 ＋ D5 兩段式，錯了只影響暫時釘 `@v1.4.1` 的 probe
- concurrency 改名：跑到一半的 run 不受影響，新 run 用新 group
- env 改寫：`"$VAR"` 只展開一次，值裡的 `$`、反引號不會再被展開；空字串照樣傳成空字串參數，行為跟原本一致
- 釘 SHA 的長期代價：action 的修正版（含安全修正）不再自動生效，要走 Dependabot PR → merge → kit 發版

## D5 要改的 probe caller（probe **main**，2026-09-26 讀過原文）

| 檔案 | 改成 `@v1.4.1` | 加 `kit-ref: v1.4.1` |
|---|---|---|
| `ai-review-collect.yml` | `reusable-ai-review-collect.yml@v1` | —（collect 沒有這個 input） |
| `ai-review-post.yml` | `reusable-ai-review-post.yml@v1` | ✅（原本沒傳，用預設 `v1`） |
| `code-review.yml` | `reusable-static-review.yml@v1`、`reusable-codeql.yml@v1` | codeql ✅；static 沒有這個 input |

改回時反向：`@v1.4.1` → `@v1`、拿掉加上去的 `kit-ref`。push 到 probe main 不會觸發任何 workflow（collect/code-review 是 `pull_request`、post 是 `workflow_run`、兩支探針是 `workflow_dispatch`）。

## 進度

- **2026-09-26 11:1x UTC**：PR #39（α，`095d389`）、#40（β，`6845779`＋`dea19eb`）開好；本機 `git merge-tree` 確認兩者 CHANGELOG 合併不衝突
  - D1 ✅ selftest red-green：改前 [18]「釘 SHA」FAIL 37 處、「run 內插」FAIL 6 處（位置＝那 6 處），「非空」「探針」PASS；改後 100/100
  - D2 ✅ actionlint 1.7.12（含 shellcheck）十支乾淨
  - D3 ✅ 再補一層：#39 的 02 log 另外下載了 `actions/cache@9255dc7…`、`actions/checkout@8e8c483…`，來源是 `setup-trivy@3fb12ec` 內部（composite，`cache/restore`、`checkout`、`cache/save` 都釘 SHA）⇒ trivy-action → setup-trivy → cache/checkout 三層全是 SHA
  - D4 ✅ #39 run `36238481159`（01）／`36238481165`（02）的 `Download action repository` 全部是新 SHA，沒有 `@v` 開頭的
  - 04 第一輪：#39 3 筆、#40 0 筆。#39 三筆全針對 selftest 新函式，**0 筆成立**（`scratchpad` 的 `verify_pr39_findings.py`：PyYAML 當 ground truth，main 版十支 workflow 我們的函式與 PyYAML 完全一致）。但 F2 的修法（key_col 只算前導空白）**照改會誤報，而原探針對它照樣全過** → 補探針（`f99613c`），驗過照建議改會多抓到 `env:` 那一行而 FAIL
- **2026-09-26 11:30–11:37 UTC（子超授權「一次到底」，任一預期不符就停）**
  - #39 squash `554e590`（11:30:49）、#40 squash `f61c35e`（11:31:09）、發版 #41 squash `2570d55`（11:36:25）；三個都用 `--match-head-commit`，merge 後比 tree 全部一致，本機與遠端 branch 已刪
  - `v1.4.1` = `96c5bf9`（annotated）→ `2570d55`，只 push 這個 tag；**`v1` 仍指 v1.4.0，Release 未建**
  - check.sh 先拿 09-24 v1.4.0 回歸的三個 run 跑過：R1–R7 與當時紀錄一致；[8] 列出 7 個非 SHA 引用、[9] 空 ⇒ 兩項分得出新舊版
  - 11:37:14–17 probe main 三支 caller 改釘 `@v1.4.1`（`d952e23`／`4ba6165`／`cb6d6dd`），原文在 `probe-orig/`
  - 11:37:38 Phase S 觸發（trigger `d7ace96`）
  - ⚠️ `cd <實驗目錄> && …` 又把 harness 的主要工作目錄換走一次（RESUME harness 事實⑤）
- ~~⚠️ session 中斷時的還原~~（已不需要：11:42 全部還原完）：probe caller 用 `python3 probe_callers.py restore`（逐字比對原文）；Actions 政策照上游 SSOT「還原」段
- **11:37–11:43 UTC D5 兩段式**：Phase S 9/9 → 開 `sha_pinning_required` 跑 Phase E 6/6 ＋ 同設定下 dispatch 舊版當正向對照 2/2 → 11:42:13 政策還原（字串比對一致）→ 11:42:20–24 caller 還原（`12f3365`／`31fdf3b`／`b0ad296`，逐字比對一致）→ 建 `v1.4.1` Release（Latest）→ 11:42:51 `v1` → `96c5bf9` → Phase F 7/7。明細在 `expectations.md`
  - 順手改 v1.4.0 的 Release body：從 CHANGELOG 複製過去的「見 `[Unreleased]`」在 `[Unreleased]` 清空後指錯地方 → 改成「見 `[1.4.1]`」（改完 Latest 仍是 v1.4.1）
- **11:45–11:48 UTC D8**：PR #42（`docs/sha-pinning-supported`，`e482789`）改掉 USAGE「第 2 步」4 處與 README §7 的「目前不能用」＋ CHANGELOG `[Unreleased]` Docs 一條；寫明沒實測到的兩件（dependency review 在 probe 是 skipped、複製路線沒在開政策的 repo 跑過）。CI 綠
  - **post 的 ④ 實跑通過**：#42 的 04 `36239895148` 用 `@refs/tags/v1 (96c5bf9…)` → `HEAD is now at 2570d55`，「貼回 PR」step 印出 `MIN_SEVERITY: minor`／`MIN_CONFIDENCE: 0.7`／`MAX_INLINE: 8`，success，findings=1、inline=1
  - 那 1 筆（Minor 0.75，USAGE:35「正常」一詞）**不成立**：原文用分號把 `sha_pinning_required` 另起一句、寫的是「都可以」，它建議的用詞已經在文件裡 → [[annotated-code-review-blindspot]] 同型
- **新發現：post 的 ④（`MIN_SEVERITY` 等 3 處）probe 驗不到**（已由 D8 補上，見上）。probe 的 post 在 401 停下，走不到「貼回 PR」那一步（`if:` 隱含 `success()`）。static 的 ④ 驗得到（probe 傳 `lint-name: shellcheck`）。post 的 ④ 要等 `v1` 移動後，本 repo 下一個 PR（δ）的 04 用真 key 走到那一步 → 併進 D8 一起看
