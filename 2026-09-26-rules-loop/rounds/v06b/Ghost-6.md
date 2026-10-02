<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為讀取 config 的 memberWelcomeEmailTestInbox 設定，並更新相關測試。主要風險在於排程邏輯的條件反轉（jobs/index.js）可能導致重複排程或完全停止排程，以及 MemberRepository 中條件判斷的語意改變可能讓所有來源的成員都觸發歡迎郵件。建議先修正排程條件，並確認 config 值為空字串時的行為。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程或永不排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件判斷語意改變可能導致所有來源都觸發歡迎郵件 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.90 |
| 🔸 | Minor | `ghost/core/test/integration/services/member-welcome-emails.test.js:53` | 測試中設定空字串可能無法模擬未設定狀態 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程或永不排程</summary>

原條件 `!hasScheduled.processOutbox` 在尚未排程時才新增 job，修改後變成 `hasScheduled.processOutbox`，只有在已排程時才新增 job，導致首次呼叫時不會排程，後續呼叫則可能重複排程。

**失敗情境**：
1. 首次呼叫 `scheduleMemberWelcomeEmailJob()` 時，`hasScheduled.processOutbox` 為 false，條件不成立，job 永遠不會被加入。
2. 若某處將 `hasScheduled.processOutbox` 設為 true（例如手動觸發），之後每次呼叫都會再次新增 job，造成重複排程。

**建議修法**：
將條件改回 `!hasScheduled.processOutbox`，並在新增 job 後將 `hasScheduled.processOutbox` 設為 true。

**判斷依據**：diff 中將 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，且後續 `jobsService.addJob` 呼叫未變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件判斷語意改變可能導致所有來源都觸發歡迎郵件</summary>

原條件 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)` 要求 labs 旗標開啟且來源在允許清單中。修改後變成 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`，只要 config 有值或來源在清單中就成立。若 config 未設定（undefined 或空字串），但來源是允許的（例如 'member'），仍會觸發歡迎郵件，與預期「config 未設定時不寄送」的行為不符。

**失敗情境**：
- 在正式環境中，若 `memberWelcomeEmailTestInbox` 未設定，但成員來源為 'member'，系統仍會建立 outbox 條目並嘗試寄送歡迎郵件，可能造成非預期的郵件發送。

**建議修法**：
改為 `welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`，或明確檢查 config 值為非空字串。

**判斷依據**：diff 中將 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)` 改為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

此處將原本的 `let member;` 改為 `var member;`，違反專案規範 R20（應使用 let 或 const）。var 有函數作用域和提升問題，可能導致非預期行為。

**建議修法**：
改回 `let member;`。

**判斷依據**：diff 中將 `let member;` 改為 `var member;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/member-welcome-emails.test.js:53</code> 測試中設定空字串可能無法模擬未設定狀態</summary>

在測試 'does NOT create outbox entry when config is not set' 中，使用 `configUtils.set('memberWelcomeEmailTestInbox', '')` 來模擬未設定。但若程式碼中檢查的是 falsy 值（如 `if (!config.get(...))`），空字串會被視為 false，測試可能通過；但若程式碼改為檢查 `config.get(...) !== undefined`，則空字串會被視為已設定，導致測試失敗。建議使用 `configUtils.set('memberWelcomeEmailTestInbox', undefined)` 或直接刪除該設定，以更準確模擬未設定狀態。

**判斷依據**：diff 中新增此行，且對應的程式碼檢查為 `if (!config.get('memberWelcomeEmailTestInbox'))`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6540 (cache hit 6528) ｜ completion tokens 1347 ｜ PR #6</sub>