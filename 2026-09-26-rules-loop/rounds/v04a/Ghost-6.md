<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能從 labs flag 改為依賴 config 值 `memberWelcomeEmailTestInbox`，並更新相關測試。主要風險在於排程邏輯的條件反轉（`if (hasScheduled.processOutbox && ...)`）可能導致重複排程或行為異常，以及 `MemberRepository.js` 中條件判斷的邏輯變更（`welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`）可能使歡迎郵件在未預期的來源下觸發。此外，測試中使用了 `var` 違反專案規範。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程或永不排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件判斷邏輯變更可能導致非預期來源觸發歡迎郵件 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.90 |
| 🔸 | Minor | `ghost/core/test/integration/services/member-welcome-emails.test.js:53` | 測試中設定空字串可能無法模擬未設定 config 的情境 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程或永不排程</summary>

原程式碼為 `if (!hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test'))`，修改後變成 `if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test'))`。這會使得當 `hasScheduled.processOutbox` 為 `false` 時（尚未排程），條件不成立，因此永遠不會排程；而當它為 `true` 時（已排程），條件成立，又會再次排程，造成重複排程。正確邏輯應保持 `!hasScheduled.processOutbox`。

**判斷依據**：diff 中將 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，與變數名稱語意相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件判斷邏輯變更可能導致非預期來源觸發歡迎郵件</summary>

原條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，修改後為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。這表示只要 `welcomeEmailConfig` 為 truthy（例如設定了測試收件匣），無論 `source` 是否在允許清單中，都會建立 outbox 條目。這可能導致管理員建立或匯入的成員也收到歡迎郵件，與預期行為不符。建議改為 `welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`。

**判斷依據**：diff 中條件從 `&&` 改為 `||`，且 `welcomeEmailConfig` 取代了原本的 labs flag。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

專案規範禁止使用 `var`，應改用 `let` 或 `const`。此處 `var member;` 違反規範。

**判斷依據**：diff 中將 `let member;` 改為 `var member;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/member-welcome-emails.test.js:53</code> 測試中設定空字串可能無法模擬未設定 config 的情境</summary>

在測試 'does NOT create outbox entry when config is not set' 中，使用 `configUtils.set('memberWelcomeEmailTestInbox', '')` 來模擬未設定。但若程式碼中對 config 的判斷是 truthy/falsy，空字串為 falsy，可達到效果；但若未來程式碼改為檢查 `!== undefined`，則此測試可能失效。建議使用 `configUtils.set('memberWelcomeEmailTestInbox', undefined)` 或直接刪除該 config key，以更貼近未設定的情境。

**判斷依據**：diff 中該行設定為空字串，而其他測試設定為非空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5430 (cache hit 4224) ｜ completion tokens 1125 ｜ PR #6</sub>