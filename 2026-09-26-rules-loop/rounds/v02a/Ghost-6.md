<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs 旗標改為讀取 config 的 memberWelcomeEmailTestInbox 設定。主要風險在於排程任務的條件判斷被反轉（從 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`），可能導致任務重複排程或完全不被排程；此外，MemberRepository 中使用了 var 宣告，違反程式碼規範。建議優先修正排程條件邏輯並改用 let/const。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件判斷反轉，可能導致任務重複排程或永不執行 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數，應改用 let 或 const | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件判斷反轉，可能導致任務重複排程或永不執行</summary>

原本的條件 `!hasScheduled.processOutbox` 確保任務只會被排程一次，但修改後變成 `hasScheduled.processOutbox`，這會讓任務在已經排程過後再次被排程，造成重複執行；若初始值為 false，則任務永遠不會被排程。建議改回 `!hasScheduled.processOutbox`。

**判斷依據**：diff 中將 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，且 `hasScheduled` 物件在檔案開頭初始化為 `{ processOutbox: false }`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數，應改用 let 或 const</summary>

此處將原本的 `let member;` 改為 `var member;`，違反專案規範 R20（必須使用 let 或 const）。請改回 `let member;`。

**判斷依據**：diff 中明確將 `let member;` 改為 `var member;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6550 (cache hit 1536) ｜ completion tokens 554 ｜ PR #6</sub>