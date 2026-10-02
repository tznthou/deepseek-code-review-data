<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能從 labs 旗標改為以 config 值 `memberWelcomeEmailTestInbox` 控制，並調整排程條件。主要風險在於排程條件反轉可能導致重複排程，以及 config 值未驗證可能造成非預期行為。建議先修正排程邏輯並確認 config 值驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341` | config 值未驗證，可能導致非預期行為 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11` | config 值未驗證，可能導致排程邏輯錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程</summary>

原本條件 `!hasScheduled.processOutbox` 在未排程時才排程，現在改為 `hasScheduled.processOutbox`，變成已排程時才排程。這會導致：
1. 首次呼叫時 `hasScheduled.processOutbox` 為 false，不會排程。
2. 若之後某次呼叫時 `hasScheduled.processOutbox` 被設為 true（例如手動設定或未來程式碼變更），則會重複排程。
建議改回 `!hasScheduled.processOutbox`。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341</code> config 值未驗證，可能導致非預期行為</summary>

`config.get('memberWelcomeEmailTestInbox')` 的回傳值直接作為條件判斷，但未驗證其型別或內容。若 config 值為空字串、0、false 等 falsy 值，則條件為 false，不會建立 outbox；若為任意 truthy 值（例如 'false' 字串），則會建立 outbox。建議明確驗證該值是否為有效的 email 或布林值。

**判斷依據**：diff 中新增 `const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox');` 並直接以 `welcomeEmailConfig` 作為條件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11</code> config 值未驗證，可能導致排程邏輯錯誤</summary>

`config.get('memberWelcomeEmailTestInbox')` 的回傳值直接作為條件判斷，若 config 值為空字串或未定義，則不會排程；若為任意 truthy 值（例如 'false' 字串），則會排程。建議明確驗證該值是否為有效的 email 或布林值。

**判斷依據**：diff 中此行由 `if (!labs.isSet('welcomeEmails'))` 改為 `if (!config.get('memberWelcomeEmailTestInbox'))`，未對 config 值做驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4241 (cache hit 1536) ｜ completion tokens 882 ｜ PR #6</sub>