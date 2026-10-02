<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能從 labs 旗標改為以 config 值 `memberWelcomeEmailTestInbox` 控制，並更新相關測試。主要風險在於排程邏輯的條件反轉可能導致重複排程，以及 config 值語意不明可能造成非預期行為。建議先修正排程條件並確認 config 值的使用方式。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341` | config 值語意不明可能導致非預期行為 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11` | config 值可能未定義導致錯誤 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程</summary>

原本的條件 `!hasScheduled.processOutbox` 在尚未排程時才執行排程，但修改後變成 `hasScheduled.processOutbox`，這會導致當 `hasScheduled.processOutbox` 為 true 時再次排程，造成重複排程。應改回 `!hasScheduled.processOutbox`。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {` 改為 `if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {`，條件反轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341</code> config 值語意不明可能導致非預期行為</summary>

原本使用 `labs.isSet('welcomeEmails')` 檢查功能是否啟用，現在改為 `config.get('memberWelcomeEmailTestInbox')`。若此 config 值是用來指定測試收件匣，則其存在與否不應直接代表功能啟用，可能造成在正式環境中誤啟用或停用。建議確認 config 值的用途，或改用明確的布林設定。

**判斷依據**：diff 中新增 `const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox');` 並將條件改為 `if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source))`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11</code> config 值可能未定義導致錯誤</summary>

`config.get('memberWelcomeEmailTestInbox')` 若未設定可能回傳 undefined，在 `if (!config.get(...))` 中會被視為 false，但若 config 系統對未定義的 key 拋出錯誤，則可能導致啟動失敗。建議確認 config 系統行為，或使用 `config.get('memberWelcomeEmailTestInbox', false)` 提供預設值。

**判斷依據**：diff 中此行由 `if (!labs.isSet('welcomeEmails')) {` 改為 `if (!config.get('memberWelcomeEmailTestInbox')) {`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 22408 (cache hit 22400) ｜ completion tokens 858 ｜ PR #6</sub>