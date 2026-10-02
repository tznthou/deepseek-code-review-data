<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為讀取設定值 `memberWelcomeEmailTestInbox`，並調整排程條件。主要風險在於 `MemberRepository.js` 中條件邏輯的變更：原本只有在 labs 旗標開啟且來源為允許清單時才建立 outbox，現在只要設定值存在或來源為允許清單就會建立，這可能導致非預期的歡迎郵件發送。此外，排程條件從 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，邏輯完全相反，可能造成排程永遠不會執行或重複執行。測試中使用了 `sinon.stub(config, 'get')` 但未在測試後還原，可能影響其他測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件邏輯反轉，可能導致排程永不執行或重複執行 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件邏輯變更可能導致非預期的歡迎郵件發送 | 0.90 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.80 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/members/members-api/repositories/MemberRepository.test.js:530` | 測試中 stub config.get 但未在測試後還原 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件邏輯反轉，可能導致排程永不執行或重複執行</summary>

原本的條件是 `!hasScheduled.processOutbox`，表示只有在尚未排程時才新增 job；現在改為 `hasScheduled.processOutbox`，只有在已排程時才新增 job。這會導致第一次呼叫時不會排程，而後續呼叫（如果有的話）會重複排程。請確認此變更是否為筆誤，並修正為正確的條件。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，邏輯完全相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件邏輯變更可能導致非預期的歡迎郵件發送</summary>

原本條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，現在改為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。這表示只要設定值存在（即使為空字串？）或來源在允許清單中，就會建立 outbox。若設定值為空字串（falsy），則條件退化成只檢查來源，可能導致在未啟用歡迎郵件功能時仍發送郵件。請確認此邏輯是否符合預期，並考慮使用明確的布林值或檢查設定值是否為有效信箱。

**判斷依據**：diff 中此行由 `if (this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source))` 改為 `if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source))`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

此處將原本的 `let member;` 改為 `var member;`，違反了專案規範 R20（必須使用 let 或 const）。請改回 `let` 或使用 `const`（若變數不會重新賦值）。

**判斷依據**：diff 中此行由 `let member;` 改為 `var member;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/members/members-api/repositories/MemberRepository.test.js:530</code> 測試中 stub config.get 但未在測試後還原</summary>

在測試中使用 `sinon.stub(config, 'get')` 來模擬設定值，但未在測試後呼叫 `config.get.restore()` 或使用 `sinon.restore()`。這可能導致 stub 洩漏到其他測試，造成非預期的行為。請在 `afterEach` 或測試結尾還原 stub。

**判斷依據**：diff 中新增了多處 `sinon.stub(config, 'get')`，但未見對應的 restore 呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6474 (cache hit 6400) ｜ completion tokens 1159 ｜ PR #6</sub>