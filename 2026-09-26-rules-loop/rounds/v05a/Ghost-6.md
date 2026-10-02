<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為讀取設定值 `memberWelcomeEmailTestInbox`，並調整排程條件與測試。主要風險在於 `MemberRepository.js` 中條件判斷的邏輯變更：原本需同時滿足 labs 旗標與來源白名單，現在只要設定值存在或來源在白名單中即觸發，可能導致非預期的歡迎郵件發送。此外，排程條件由 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，邏輯反轉，可能造成排程永遠不會執行或重複執行。另有 `var` 取代 `let` 的風格違規。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件邏輯反轉，可能導致歡迎郵件永不發送 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 歡迎郵件觸發條件過寬，可能對非允許來源發送郵件 | 0.90 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 取代 let 宣告變數 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件邏輯反轉，可能導致歡迎郵件永不發送</summary>

原本條件為 `!hasScheduled.processOutbox`，表示尚未排程時才新增排程；改為 `hasScheduled.processOutbox` 後，只有在已排程時才會再次新增排程，但 `hasScheduled.processOutbox` 在新增排程後並未設為 true，因此條件永遠為 false，排程永遠不會被建立。

失敗情境：當 `memberWelcomeEmailTestInbox` 設定存在且 NODE_ENV 不是 test 時，`scheduleMemberWelcomeEmailJob` 被呼叫，但因為 `hasScheduled.processOutbox` 初始為 false，條件不成立，不會呼叫 `jobsService.addJob`，導致歡迎郵件永遠不會被處理。

建議改回 `!hasScheduled.processOutbox`，並在成功新增排程後將 `hasScheduled.processOutbox` 設為 true。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，且後續未見 `hasScheduled.processOutbox = true` 的設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 歡迎郵件觸發條件過寬，可能對非允許來源發送郵件</summary>

原本條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，需同時滿足 labs 旗標與來源白名單。改為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)` 後，只要設定值存在（truthy）或來源在白名單中即觸發，導致即使來源不在白名單（例如 `import` 或 `admin`），只要設定了 `memberWelcomeEmailTestInbox`，就會建立 outbox 條目。

失敗情境：管理員在設定中填入測試收件匣後，從管理後台手動新增會員（來源為 `admin`），系統會錯誤地為該會員建立歡迎郵件 outbox 條目，違反原本「僅限特定來源」的設計。

建議改為 `welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`，或明確區分測試模式與正式模式。

**判斷依據**：diff 中此行由 `if (this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source))` 改為 `if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source))`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 取代 let 宣告變數</summary>

此行將原本的 `let member;` 改為 `var member;`，違反專案規範 R20（必須使用 let 或 const）。var 有函式作用域與提升問題，可能導致非預期行為。

建議改回 `let member;`。

**判斷依據**：diff 中此行由 `let member;` 改為 `var member;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6474 (cache hit 4224) ｜ completion tokens 1121 ｜ PR #6</sub>