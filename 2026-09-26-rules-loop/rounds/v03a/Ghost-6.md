<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能的開關從 labs flag 改為 config 值，並更新相關測試。主要風險在於排程邏輯的條件反轉（`!hasScheduled.processOutbox` 改為 `hasScheduled.processOutbox`）可能導致排程永不執行或重複排程；此外，`MemberRepository` 中條件判斷的邏輯變更（`welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`）可能使歡迎郵件在未設定 config 時仍對所有來源發送，與測試預期不符。另有使用 `var` 違反專案規範。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致 job 永不執行或重複排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342` | 條件判斷邏輯變更可能導致歡迎郵件發送給所有來源 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致 job 永不執行或重複排程</summary>

原本的條件 `!hasScheduled.processOutbox` 確保 job 只會被排程一次；改成 `hasScheduled.processOutbox` 後，當 `hasScheduled.processOutbox` 為 true 時才會排程，但初始值為 false，因此 job 永遠不會被排程。若後續有其他程式碼將 `hasScheduled.processOutbox` 設為 true，則可能造成重複排程。

建議改回 `!hasScheduled.processOutbox`，或使用其他冪等機制。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，且 `hasScheduled.processOutbox` 初始值為 false（見檔案上方 `let hasScheduled = { processOutbox: false }`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342</code> 條件判斷邏輯變更可能導致歡迎郵件發送給所有來源</summary>

原本條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，表示必須同時滿足 labs flag 開啟且來源在允許清單中。新條件為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`，只要 config 有值或來源在清單中就會觸發。這表示即使 config 未設定，只要來源是允許的（例如 'member'），仍會建立 outbox entry，與測試中「config 未設定時不建立 outbox entry」的預期不符。

建議改為 `welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`，或明確區分測試模式與正式模式。

**判斷依據**：diff 中此行由 `if (this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source))` 改為 `if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source))`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

專案規範 R20 要求使用 let 或 const，禁止 var。此處將原本的 `let member;` 改為 `var member;`，違反規範。

建議改回 `let member;`。

**判斷依據**：diff 中此行由 `let member;` 改為 `var member;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6560 (cache hit 4224) ｜ completion tokens 969 ｜ PR #6</sub>