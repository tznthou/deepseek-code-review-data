<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能從 labs 旗標切換為 config 設定（memberWelcomeEmailTestInbox），並調整排程邏輯。主要風險在於排程條件反轉可能導致重複排程或未排程，以及 config 值型別不一致（空字串 vs undefined）可能造成行為差異。建議先修正排程條件並統一 config 值處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉，可能導致重複排程或未排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341` | config 值型別不一致可能導致行為差異 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11` | config 值可能為空字串時仍會嘗試排程 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉，可能導致重複排程或未排程</summary>

原本的條件 `!hasScheduled.processOutbox` 在尚未排程時才進行排程，但修改後變成 `hasScheduled.processOutbox`，導致只有在已排程時才會再次排程，造成重複排程；若尚未排程則永遠不會排程。

失敗情境：當 `hasScheduled.processOutbox` 為 false 時，函式直接回傳 false，不會呼叫 `jobsService.addJob`，因此歡迎郵件排程永遠不會被建立。

建議改回 `!hasScheduled.processOutbox`。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，條件反轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341</code> config 值型別不一致可能導致行為差異</summary>

在測試中，未設定時使用 `configUtils.set('memberWelcomeEmailTestInbox', '')`（空字串），而單元測試中 stub 回傳 `undefined`。在程式碼中，`welcomeEmailConfig` 若為空字串，`if (welcomeEmailConfig || ...)` 會視為 falsy，因此不會觸發歡迎郵件；但若 config 實際回傳 `undefined`，行為相同。然而，若 config 回傳其他 falsy 值（如 `null`、`0`），行為可能不同。建議統一 config 的預設值，並在程式碼中明確檢查是否為有效字串。

失敗情境：若 config 設定為空字串，且 `WELCOME_EMAIL_SOURCES.includes(source)` 為 false，則不會建立 outbox；但若 config 設定為 `null`，`welcomeEmailConfig` 為 null，`if (null || ...)` 仍會進入，可能造成非預期行為。

**判斷依據**：diff 中新增 `const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox');` 並使用 `if (welcomeEmailConfig || ...)`，但測試中對 config 的設定值不一致（空字串 vs undefined）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11</code> config 值可能為空字串時仍會嘗試排程</summary>

`config.get('memberWelcomeEmailTestInbox')` 若回傳空字串，`!config.get(...)` 為 true，因此會進入排程邏輯。但空字串可能代表未設定，不應排程。建議明確檢查 config 值是否為有效字串（非空）。

失敗情境：若 config 設定為空字串，且 `hasScheduled.processOutbox` 為 false（假設條件修正後），仍會排程，但實際上不應發送歡迎郵件。

**判斷依據**：diff 中此行由 `if (!labs.isSet('welcomeEmails'))` 改為 `if (!config.get('memberWelcomeEmailTestInbox'))`，未處理空字串情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4241 (cache hit 4224) ｜ completion tokens 1068 ｜ PR #6</sub>