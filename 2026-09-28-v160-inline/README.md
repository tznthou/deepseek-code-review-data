# v1.6.0：inline 預設關閉 ＋ kit-selftest 成為必要檢查（2026-09-28）

來源：同日評分（66→64）與 /pi-askall（Codex 61、agy 60）的共同建議，子超「同意建議，改」。
計畫：`.claude/plans/2026-09-28-review-followups.md`（計畫審查（深度模式）：第一版可逆性 FAIL → 修正後重審全 PASS）。
時間一律 UTC。

## 結果

- **A（kit-selftest 必要檢查）完成**：#53 `ac91001`；ruleset `24099358`「main: kit selftest 必須通過」（context `selftest`、
  integration 15368、strict 關、無 bypass），讀回 `rules/branches/main` 確認生效；#54 起 `gh pr checks --required` 只列 `selftest`
- **B（v1.6.0）完成**：#54 feature → #55 發版（`49a5975`，tag object `40c2a78`）→ probe P 12/12＋R 1/1 → #56 04 暫釘 →
  #57 自己的 AI review 驗新預設 → **`v1` 移動 06:19:10**、Release Latest 06:19:16 → #57 merge（`e2cbce3`）→ probe F 8/8
- **probe 合計 21/21，$0**；main 的 CodeQL open 0（06:19:59 run，`e2cbce3`）
- **C 只寫大綱**（計畫檔 C 段），待辦順序在 RESUME 改

## A：紅綠對照（#53 draft 期間）

| commit | 內容 | selftest | ruff | run |
|---|---|---|---|---|
| `2bb5c8f` | 本 PR | ✅（runner Python 3.12.3） | ✅ | success |
| `7451d85` | `post_review.py` 的 MARKER 改一個字＋`import textwrap` 沒用到 | ❌ golden「inline 內文逐字相同」 | ❌ F401 | failure |
| `340aded` | revert | ✅ | ✅ | success |

- 用 draft 做：`03` 的 `skip-draft` 預設 true，draft 期間不觸發 AI review（不然紅燈 commit 會多一輪要逐筆驗證的假問題）
- 紅燈 commit 先在本機確認會失敗才推；**等紅燈那次 run 跑完才推 revert**（PR 上 concurrency 會取消舊 run，先推就看不到紅燈）
- ruff 步驟 `if: success() || failure()`：紅燈那次兩步都回報

## B：selftest [22] 紅綠

新測項 9 項在改動前的 `post_review.py`／workflow 上：8 項 FAIL（`--no-inline` 被 argparse 拒絕 rc=2；workflow 沒有 input），
對照組「不帶旗標會查冪等並貼行內」兩版都 PASS；[21] 的 6 項 golden 在舊版上照舊 PASS。用 `git show main:<path> >` 換回舊檔，不用 stash。

## B：新預設的真 caller 驗收（#57 自己的 AI review，04 run `36385711510`，06:17）

- `reusable-ai-review-post.yml@refs/tags/v1.6.0 (40c2a78…)`；`HEAD is now at 49a5975 chore: 發布 v1.6.0 (#55)`
- log：`findings=2 inline=off`、`inline 關閉（--no-inline）：只貼摘要，不查既有留言`、`完成：inline 0 筆已張貼`
- PR 上 review comments 0 則；review 只有 1 則（沒貼行內就不會多出那則空 review）
- 摘要：Findings（2 筆）表＋details＋「違反 repo 規範（1 筆）」；沒有「未張貼為 inline 的 finding」

## probe（預期表 `probe-expectations.md` 跑前定稿）

- Phase P：caller 暫釘 `@v1.6.0`＋`kit-ref`，post 傳 `inline-comments: true`；觸發 `f9f69c5`（06:09:51）；
  runs collect `36385101991`、code review `36385102150`、post `36385119759` → **12/12**（`probe-P-result.txt`）
- R1：三支 caller 逐字還原（06:11:45–49）
- Phase F：`v1` 移動後、原本的 `@v1` caller（沒傳新 input）；觸發 `ec08930`（06:20:32）；
  runs `36385983506`／`36385983527`／`36386000816` → **8/8**（`probe-F-result.txt`）
- 腳本：`scripts/probe_v160.py`（stage／restore／show）、`scripts/check_probe.py`、`scripts/check_probe_f.py`；
  觸發沿用 `../2026-09-26-v1.4.1/commit.py`
- ⚠️ `check_probe_f.py` 用 sed 從 v1.5.0 版改寫時，F2 的替換在 zsh one-liner 裡跳脫錯、沒換到；跑之前 grep 看出來、改用 Edit

## 這一輪的 AI review（逐筆驗證）

| PR | 筆數 | 成立 | 貼成 inline | 內容 |
|---|---|---|---|---|
| #53 | 2 | 0 | 2 | 「push 沒限制 branches」（下一行就是 `branches: [main]`）、「ruff 被取消時不跑」（刻意） |
| #54 | 1 | 0 | 1 | 「`INLINE_COMMENTS` 空字串時 `[ ]` 報 unary operator expected」：變數有加引號，bash 實測不報錯；沒傳 input 是預設 false |
| #55 | 0 | — | — | verdict=approve |
| #56 | 2 | 0 | 1 | 一般 0.60「可變 tag 應釘 SHA」（沒過門檻）＋規範 [R01] 0.90（貼 inline）——都是本 repo 自己的 reusable workflow |
| #57 | 3 | 0（1 部分） | 0（inline 已關） | 「移 v1 前不能 merge」部分成立（已在流程；機制講成靜默忽略，實為 startup_failure）；「inline 多 API 呼叫」不成立；[R01] 0.95 不成立 |

合計 8 筆：0 成立、1 部分成立；貼成 inline 的 4 筆全部不成立。

## 觀察（待 RESUME 處理）

- **R01 收窄後連續誤套 2 次**（#56、#57）：規範檔 R01 寫明「本 repo 自己的 reusable workflow 用 tag 引用是刻意的，不在此限」，
  模型兩次都照樣標 R01（0.90／0.95）。#51 當時的判斷是「文字歧義，不是規範那次誤套過（#50 四次 0 筆）」——現在有了 2 筆實例。
  兩次都在 04 暫釘／改回的 PR 上（diff 正好碰到那行）
  → **09-30 子超裁定拿掉 R01，PR #58**；編號重排（原 R02–R11 → R01–R10），細節在 `2026-09-28-v150-repo-rules/README.md`「kit 規範檔拍板」
- **規範那次第一次在真實 PR 上標出有效編號**（#56）：摘要的「違反 repo 規範」表、單獨貼出的行內留言（sub 行帶規範全文）都照設計
- **跨 pass 合併第一次在正式環境執行到**（#57，`merged=1`），但 inline 關閉，沒貼出去；合併留言的真實長相仍待 04 opt-in 之後的 PR
- log 小瑕疵：`--no-inline` 時規範那行仍印 `inline=1 merged=1`（是 `select_inline` 的結果，不是實際貼出），主行已印 `inline=off`
- **待（被動）**：04 打開 `inline-comments: true` 之後的第一個 PR，驗行內留言照貼（opt-in 路徑的真 caller 驗收）
  → **09-30 #58（run `36668105573`）只驗到一半**：旗標有接上（`inline=0` 不是 `off`、沒有「inline 關閉」那行、`完成：inline 0 筆已張貼`），但兩次呼叫都 0 筆，真的貼一則行內留言那段沒走到 → 繼續等有 ≥ 門檻 finding 的 PR
- **`v1` 移動後 04 第一次真跑 = #58**：`Uses: …@refs/tags/v1 (40c2a78…)`、success、摘要照貼（review 04:16:52 UTC）、無 `##[warning]` → 回退劇本 04 那半沒觸發；**私有 caller 那半仍沒跑**
