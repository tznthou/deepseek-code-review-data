<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為讀取 config 中的 `memberWelcomeEmailTestInbox`，並調整了排程邏輯與相關測試。主要風險在於 `jobs/index.js` 中排程條件邏輯的變更可能導致重複排程或行為不一致，以及 `MemberRepository.js` 中條件判斷的變更可能使歡迎郵件在非測試情境下意外啟用。建議先確認 config 值的來源與預設值，並修正排程條件。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件邏輯反轉，可能導致重複排程或永不排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件判斷變更可能導致歡迎郵件在非測試情境下意外啟用 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11` | config 值可能未定義或型別不符，導致排程行為不穩定 | 0.80 |
| 🔸 | Minor | `ghost/core/test/integration/services/member-welcome-emails.test.js:53` | 測試中 config 設定為空字串，可能無法正確模擬未設定狀態 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件邏輯反轉，可能導致重複排程或永不排程</summary>

原本的條件是 `!hasScheduled.processOutbox`（尚未排程時才排程），但改為 `hasScheduled.processOutbox`（已排程時才排程）。這會導致：
1. 若 `hasScheduled.processOutbox` 初始為 `false`，則永遠不會排程。
2. 若因某些原因被設為 `true`，則每次呼叫都會重複排程，造成多個排程任務。
建議改回 `!hasScheduled.processOutbox`，或明確使用一個獨立的旗標來避免重複排程。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件判斷變更可能導致歡迎郵件在非測試情境下意外啟用</summary>

原本條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，現在改為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。這表示只要 `memberWelcomeEmailTestInbox` 有值（即使不是測試環境），就會對所有來源（包括 admin、import）建立 outbox 記錄，可能造成非預期的郵件發送。建議改為 `welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`，或明確限制僅在測試環境或特定來源下啟用。

**判斷依據**：diff 中此行由 `if (this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source))` 改為 `if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source))`，邏輯運算子由 `&&` 改為 `||`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11</code> config 值可能未定義或型別不符，導致排程行為不穩定</summary>

`config.get('memberWelcomeEmailTestInbox')` 的回傳值可能為 `undefined`、空字串或非布林值。若為 `undefined`，`!undefined` 為 `true`，會嘗試排程；若為空字串，`!''` 為 `true`，同樣會排程。這可能導致在未設定該 config 時仍會排程。建議明確檢查 config 值是否為有效字串或布林值，例如 `if (!config.get('memberWelcomeEmailTestInbox'))` 改為 `if (!config.get('memberWelcomeEmailTestInbox') || config.get('memberWelcomeEmailTestInbox') === '')` 或使用更嚴謹的判斷。

**判斷依據**：diff 中此行由 `if (!labs.isSet('welcomeEmails'))` 改為 `if (!config.get('memberWelcomeEmailTestInbox'))`，未處理 config 值可能為空字串或 undefined 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/member-welcome-emails.test.js:53</code> 測試中 config 設定為空字串，可能無法正確模擬未設定狀態</summary>

在測試 `does NOT create outbox entry when config is not set` 中，使用 `configUtils.set('memberWelcomeEmailTestInbox', '')` 來模擬未設定。但若程式碼中對空字串的處理與 `undefined` 不同，此測試可能無法涵蓋真實的未設定情境。建議使用 `configUtils.set('memberWelcomeEmailTestInbox', undefined)` 或直接刪除該 config 鍵，以更貼近實際未設定的情況。

**判斷依據**：diff 中此行新增，且測試名稱強調 'config is not set'，但設定為空字串可能與未設定（undefined）行為不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4205 (cache hit 4096) ｜ completion tokens 1331 ｜ PR #6</sub>