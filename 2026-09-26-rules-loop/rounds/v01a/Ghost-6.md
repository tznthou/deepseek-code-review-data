<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為 config 設定（memberWelcomeEmailTestInbox），並更新相關測試。主要風險在於排程邏輯的條件反轉（jobs/index.js）可能導致重複排程或完全停止排程，以及 MemberRepository 中條件判斷的語意變更可能讓非測試收件匣的來源也觸發歡迎郵件。此外，程式碼中使用了 var 宣告，違反專案規範 R20。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程或完全停止排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件判斷語意變更可能導致非測試收件匣也觸發歡迎郵件 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程或完全停止排程</summary>

原本的條件 `!hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` 確保只在尚未排程且非測試環境時才新增 job。改成 `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` 後，只有在 `hasScheduled.processOutbox` 為 true 時才會排程，但該變數初始為 false，且從未在程式碼中設為 true，因此實際上永遠不會排程。這會導致歡迎郵件完全無法寄出。

建議改回原本的條件，或修正為 `!hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')`。

**判斷依據**：diff 中將 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，且 `hasScheduled` 物件在檔案開頭初始化為 `{ processOutbox: false }`，沒有其他地方將其設為 true。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件判斷語意變更可能導致非測試收件匣也觸發歡迎郵件</summary>

原本的條件 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)` 要求 labs 旗標開啟且來源在允許清單中。改成 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)` 後，只要 config 有值或來源在清單中就會觸發，即使 config 未設定（例如空字串或 undefined）且來源在清單中，也會建立 outbox 條目。這可能導致在未啟用歡迎郵件功能時仍寄出郵件。

建議改為 `welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`，或明確檢查 config 是否為有效值。

**判斷依據**：diff 中將 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)` 改為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

程式碼中將 `let member;` 改為 `var member;`，違反專案規範 R20（必須使用 let 或 const）。var 有函數作用域和提升問題，可能導致非預期行為。

建議改回 `let member;` 或使用 `const`（如果不需要重新賦值）。

**判斷依據**：diff 中將 `let member;` 改為 `var member;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6550 (cache hit 4224) ｜ completion tokens 981 ｜ PR #6</sub>