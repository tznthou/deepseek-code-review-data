<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為讀取 config 的 memberWelcomeEmailTestInbox 設定，並更新相關測試。主要風險在於排程邏輯的條件反轉（jobs/index.js）可能導致重複排程或完全停用，且 MemberRepository 的條件判斷從 AND 改為 OR 可能讓所有來源的成員都觸發歡迎郵件，造成非預期的郵件發送。建議先修正排程條件與確認來源限制邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程或功能停用 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件判斷從 AND 改為 OR 可能導致非預期發送歡迎郵件 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程或功能停用</summary>

原條件 `!hasScheduled.processOutbox` 確保只排程一次，但改為 `hasScheduled.processOutbox` 後，當 `hasScheduled.processOutbox` 為 true 時才會排程，這與變數名稱語意相反。若 `hasScheduled.processOutbox` 初始為 false，則永遠不會排程；若在某處被設為 true，則每次呼叫都會重複排程。

建議改回 `!hasScheduled.processOutbox`，或將變數名稱改為 `hasScheduled` 並正確設定其值。

**判斷依據**：diff 中將 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，但變數名稱仍為 `hasScheduled`，邏輯矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件判斷從 AND 改為 OR 可能導致非預期發送歡迎郵件</summary>

原條件 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)` 要求兩者皆真，但改為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)` 後，只要來源在允許清單中（例如 'member'），即使 config 未設定也會觸發歡迎郵件。這可能導致在未設定測試收件匣時，所有符合來源的成員建立都會嘗試發送歡迎郵件，造成非預期的郵件發送。

建議改為 `welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`，或明確說明為何要放寬條件。

**判斷依據**：diff 中將 `&&` 改為 `||`，且 `welcomeEmailConfig` 來自 config，可能為空字串或 undefined。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

此處將原本的 `let member;` 改為 `var member;`，違反專案規範 R20（應使用 let 或 const）。var 有函數作用域與提升問題，可能導致非預期行為。

建議改回 `let member;`。

**判斷依據**：diff 中明確將 `let member;` 改為 `var member;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5430 (cache hit 5376) ｜ completion tokens 910 ｜ PR #6</sub>