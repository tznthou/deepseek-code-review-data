<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為 config 設定 `memberWelcomeEmailTestInbox`，並調整排程邏輯。主要風險在於排程條件反轉可能導致重複排程，以及 config 值型別不一致（空字串 vs undefined）可能造成行為不一致。建議先修正排程條件並統一 config 值處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341` | config 值型別不一致可能導致判斷錯誤 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程</summary>

原本條件 `!hasScheduled.processOutbox` 在尚未排程時才新增 job，但改為 `hasScheduled.processOutbox` 後，變成已排程時才新增 job，導致每次呼叫都會重複新增 job，造成資源浪費與潛在的重複執行。

建議改回 `!hasScheduled.processOutbox`，或在新增 job 後立即設定 `hasScheduled.processOutbox = true`。

**判斷依據**：diff 中將 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，且 `hasScheduled` 物件在檔案開頭定義，未見其他更新邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341</code> config 值型別不一致可能導致判斷錯誤</summary>

`config.get('memberWelcomeEmailTestInbox')` 可能回傳空字串、undefined 或其他 falsy 值，但程式碼僅以 `welcomeEmailConfig ||` 判斷，未明確處理空字串與 undefined 的差異。若設定為空字串，條件為 false，但若設定為其他 falsy 值（如 0）也會被視為未啟用，可能與預期不符。

建議使用明確的檢查，例如 `if (welcomeEmailConfig !== undefined && welcomeEmailConfig !== '')`，或統一設定值的型別。

**判斷依據**：diff 中新增 `const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox');` 並以 `welcomeEmailConfig ||` 判斷。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

此處將原本的 `let member;` 改為 `var member;`，違反專案規範 R20（應使用 let 或 const）。

建議改回 `let member;`。

**判斷依據**：diff 中將 `let member;` 改為 `var member;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6550 (cache hit 6528) ｜ completion tokens 820 ｜ PR #6</sub>