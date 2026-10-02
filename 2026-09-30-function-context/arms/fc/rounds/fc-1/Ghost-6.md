<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為 config 設定 `memberWelcomeEmailTestInbox`，並調整排程邏輯與相關測試。主要風險在於排程條件反轉可能導致重複排程、config 值型別不一致（字串 vs 布林）造成的行為差異，以及測試中直接 stub `config.get` 可能影響其他測試。建議先確認排程邏輯與 config 型別。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341` | config 值型別不一致可能導致條件判斷錯誤 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/members/members-api/repositories/MemberRepository.test.js:14` | 測試中直接 stub config.get 可能影響其他測試 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程</summary>

原本條件為 `!hasScheduled.processOutbox`，修改後變成 `hasScheduled.processOutbox`，這會導致當 `hasScheduled.processOutbox` 為 true 時再次呼叫 `jobsService.addJob`，造成重複排程。應改回 `!hasScheduled.processOutbox`。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341</code> config 值型別不一致可能導致條件判斷錯誤</summary>

`config.get('memberWelcomeEmailTestInbox')` 在測試中被設定為字串（如 'test-inbox@example.com'）或空字串，但在程式碼中直接作為布林條件使用。若 config 值為空字串，`welcomeEmailConfig` 為 falsy，但 `WELCOME_EMAIL_SOURCES.includes(source)` 仍可能為 true，導致非預期建立 outbox。建議明確檢查 config 值是否為非空字串，或統一型別。

**判斷依據**：diff 中新增 `const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox');` 並以 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)` 作為條件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/members/members-api/repositories/MemberRepository.test.js:14</code> 測試中直接 stub config.get 可能影響其他測試</summary>

在測試中使用 `sinon.stub(config, 'get')` 直接替換全域 config 物件的 get 方法，且未在 afterEach 中 restore（僅有 `sinon.restore()` 在 describe 層級）。這可能導致其他測試意外使用到 stub 的 config.get，造成測試汙染。建議使用 sandbox 或確保每個測試後還原。

**判斷依據**：diff 中新增此 stub，且未見對應的 restore 邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 22408 (cache hit 1536) ｜ completion tokens 860 ｜ PR #6</sub>