<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為 config 設定 `memberWelcomeEmailTestInbox`，並調整排程邏輯。主要風險在於排程條件反轉可能導致重複排程或完全停用，以及 config 值型別不一致（字串 vs 布林）可能造成非預期行為。建議先修正排程條件並統一 config 值型別。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程或完全停用 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341` | config 值型別不一致可能導致非預期行為 | 0.80 |
| 🔸 | Minor | `ghost/core/test/integration/services/member-welcome-emails.test.js:53` | 測試中 config 設定為空字串可能無法模擬未設定狀態 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程或完全停用</summary>

原本條件 `!hasScheduled.processOutbox` 確保只排程一次，但改為 `hasScheduled.processOutbox` 後，當 `hasScheduled.processOutbox` 為 true 時會再次排程，造成重複排程；若為 false 則永遠不排程。應改回 `!hasScheduled.processOutbox`。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {` 改為 `if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {`，條件反轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341</code> config 值型別不一致可能導致非預期行為</summary>

`config.get('memberWelcomeEmailTestInbox')` 回傳值可能是字串（如測試中設定的 'test-inbox@example.com'）或 undefined。在條件判斷中，空字串會被視為 falsy，但非空字串為 truthy，因此若設定為空字串會停用功能，但設定為任意非空字串（即使不是有效 email）也會啟用。建議明確檢查是否為有效 email 或使用布林值。

**判斷依據**：diff 中新增 `const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox');` 並以 `if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source))` 判斷，未驗證 config 值型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/member-welcome-emails.test.js:53</code> 測試中 config 設定為空字串可能無法模擬未設定狀態</summary>

在測試 'does NOT create outbox entry when config is not set' 中，使用 `configUtils.set('memberWelcomeEmailTestInbox', '')` 模擬未設定，但若程式碼中檢查的是 `config.get(...)` 回傳 undefined，空字串可能被視為 falsy 而通過，但若未來程式碼改為檢查 `!== undefined` 則測試會失效。建議使用 `configUtils.set('memberWelcomeEmailTestInbox', undefined)` 或刪除設定。

**判斷依據**：diff 中此行將原本的 `sinon.stub(labs, 'isSet').withArgs('welcomeEmails').returns(false);` 改為 `configUtils.set('memberWelcomeEmailTestInbox', '');`，但未明確模擬 undefined。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4205 (cache hit 1408) ｜ completion tokens 947 ｜ PR #6</sub>