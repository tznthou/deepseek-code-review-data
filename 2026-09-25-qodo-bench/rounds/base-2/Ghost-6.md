<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能從 labs 旗標改為以 config 值 `memberWelcomeEmailTestInbox` 控制，並調整排程邏輯與測試。主要風險在於排程條件反轉可能導致重複排程或永不排程，以及 config 值型別不一致（字串 vs 布林）可能造成非預期行為。建議先修正排程邏輯並統一 config 值型別。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程或永不排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341` | config 值型別不一致可能導致非預期行為 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件邏輯變更可能導致非預期來源觸發歡迎郵件 | 0.75 |
| 🔸 | Minor | `ghost/core/test/integration/services/member-welcome-emails.test.js:53` | 測試中 config 設定為空字串可能無法模擬未設定狀態 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程或永不排程</summary>

原本的條件 `!hasScheduled.processOutbox` 在尚未排程時才排程，修改後變成 `hasScheduled.processOutbox`，這會導致：
1. 若 `hasScheduled.processOutbox` 為 false（尚未排程），則不會排程，功能失效。
2. 若為 true（已排程），則每次呼叫都會重複排程，造成多個重複的 job。
建議改回 `!hasScheduled.processOutbox`，或在排程後正確設定旗標。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341</code> config 值型別不一致可能導致非預期行為</summary>

`config.get('memberWelcomeEmailTestInbox')` 在測試中設定為字串（如 `'test-inbox@example.com'`）或空字串，但此處直接作為布林條件使用。若 config 值為空字串，則為 falsy，行為正確；但若為非空字串，則為 truthy，會觸發歡迎郵件。然而，若 config 值為布林 `true` 或 `false`，則行為可能與預期不同。建議明確檢查 config 值是否為非空字串，或統一使用布林值。

**判斷依據**：diff 中新增 `const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox');` 並在條件中使用，但未驗證型別。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件邏輯變更可能導致非預期來源觸發歡迎郵件</summary>

原本條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，修改後為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。這表示只要 config 有值，無論來源為何都會觸發歡迎郵件，即使來源不在允許清單中。若 config 用於測試收件匣，可能導致所有來源（如 import、admin）都寄送歡迎郵件，與預期不符。建議保留來源檢查：`welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`。

**判斷依據**：diff 中條件由 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)` 改為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/member-welcome-emails.test.js:53</code> 測試中 config 設定為空字串可能無法模擬未設定狀態</summary>

在測試 `does NOT create outbox entry when config is not set` 中，使用 `configUtils.set('memberWelcomeEmailTestInbox', '')` 來模擬未設定。但若實際 config 未設定時，`config.get` 可能回傳 `undefined` 而非空字串，兩者在條件判斷中皆為 falsy，行為相同。然而，若程式碼未來對 `undefined` 和空字串有不同處理，此測試可能無法捕捉。建議使用 `configUtils.set('memberWelcomeEmailTestInbox', undefined)` 或直接刪除該 config key。

**判斷依據**：diff 中此行設定空字串，但未驗證與未設定的差異。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4241 (cache hit 4224) ｜ completion tokens 1251 ｜ PR #6</sub>