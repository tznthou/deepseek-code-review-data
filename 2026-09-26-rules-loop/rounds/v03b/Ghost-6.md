<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為讀取 config 的 memberWelcomeEmailTestInbox 設定，並更新相關測試。主要風險在於 jobs/index.js 中排程條件的邏輯反轉（原本 !hasScheduled 改為 hasScheduled），可能導致排程永不執行或重複排程；此外 MemberRepository.js 中條件判斷從 AND 改為 OR，可能讓非允許來源的成員也觸發歡迎郵件。另有 var 宣告違反專案規範 R20。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件邏輯反轉，可能導致歡迎郵件永不發送或重複排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件判斷從 AND 改為 OR，可能讓非允許來源的成員也觸發歡迎郵件 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數，違反專案規範 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件邏輯反轉，可能導致歡迎郵件永不發送或重複排程</summary>

原本條件為 `!hasScheduled.processOutbox`，表示尚未排程時才加入 job；改為 `hasScheduled.processOutbox` 後，只有已排程時才會再次加入 job，這會造成：
1. 首次呼叫時 `hasScheduled.processOutbox` 為 false，不會排程，歡迎郵件永遠不會發送。
2. 若之後某次呼叫時 `hasScheduled.processOutbox` 被設為 true（但此處從未設定），則會重複加入 job，可能造成重複發送。
建議改回 `!hasScheduled.processOutbox`，並在加入 job 後設定 `hasScheduled.processOutbox = true`。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，且前後文未見對 `hasScheduled.processOutbox` 的賦值，邏輯明顯錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件判斷從 AND 改為 OR，可能讓非允許來源的成員也觸發歡迎郵件</summary>

原本條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，表示必須同時滿足 labs 旗標開啟且來源在允許清單中。改為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)` 後，只要 config 有設定（例如測試信箱），無論來源為何都會觸發歡迎郵件，這可能導致管理員建立或匯入的成員也收到歡迎郵件，與預期行為不符。建議改為 `welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`。

**判斷依據**：diff 中此行由 `if (this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source))` 改為 `if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source))`，邏輯運算子由 AND 改為 OR。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數，違反專案規範</summary>

專案規範 R20 要求使用 let 或 const 取代 var。此處將原本的 `let member;` 改為 `var member;`，違反規範。建議改回 `let member;`。

**判斷依據**：diff 中此行由 `let member;` 改為 `var member;`，且專案規範 R20 明確禁止 var。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6560 (cache hit 6528) ｜ completion tokens 989 ｜ PR #6</sub>