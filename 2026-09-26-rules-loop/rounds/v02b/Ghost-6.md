<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 將歡迎郵件的開關從 labs 旗標改為讀取 config 的 memberWelcomeEmailTestInbox，並更新了相關測試。主要風險在於 jobs/index.js 的排程條件邏輯被反轉（原本是 !hasScheduled.processOutbox，現在變成 hasScheduled.processOutbox），這會導致排程永遠不會被建立，除非 hasScheduled.processOutbox 為 true，但該變數初始為 false 且沒有其他地方會設為 true，因此歡迎郵件排程功能將完全失效。另外 MemberRepository.js 中使用了 var 宣告，違反了專案規範 R20。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件邏輯反轉導致歡迎郵件排程永遠不會被建立 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件邏輯反轉導致歡迎郵件排程永遠不會被建立</summary>

原本的條件是 `if (!hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test'))`，現在改成了 `if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test'))`。`hasScheduled.processOutbox` 初始值為 false，且在此函式中沒有被設為 true 的地方，因此這個條件永遠為 false，`jobsService.addJob` 永遠不會被執行，歡迎郵件排程功能將完全失效。建議改回 `!hasScheduled.processOutbox`，或在建立排程後將 `hasScheduled.processOutbox` 設為 true。

**判斷依據**：diff 中將 `!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`，且 `hasScheduled` 物件在檔案開頭定義為 `{ processOutbox: false }`，沒有其他賦值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

此處將原本的 `let member;` 改為 `var member;`，違反了專案規範 R20（必須使用 let 或 const）。請改回 `let member;`。

**判斷依據**：diff 中 `-        let member;` 被改為 `+        var member;`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6550 (cache hit 6528) ｜ completion tokens 644 ｜ PR #6</sub>