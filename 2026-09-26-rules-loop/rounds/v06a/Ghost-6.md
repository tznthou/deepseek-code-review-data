<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將歡迎郵件功能從 labs 旗標切換為 config 設定，並更新相關測試。主要風險在於排程邏輯的條件反轉可能導致重複排程，以及 config 值未驗證可能造成非預期行為。建議先修正排程條件並確認 config 值的型別與驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15` | 排程條件反轉導致重複排程 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341` | config 值未驗證型別，可能造成非預期行為 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340` | [R20] 使用 var 宣告變數 | 0.90 |
| 🔸 | Minor | `ghost/core/test/integration/services/member-welcome-emails.test.js:53` | 測試中設定空字串可能無法模擬未設定狀態 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15</code> 排程條件反轉導致重複排程</summary>

原本條件 `!hasScheduled.processOutbox` 在尚未排程時才排程，修改後變成 `hasScheduled.processOutbox`，導致已排程時又重複排程。這會造成多個排程任務同時執行，可能重複發送歡迎郵件。

建議改回 `!hasScheduled.processOutbox`，或使用其他冪等機制。

**判斷依據**：diff 中此行由 `if (!hasScheduled.processOutbox && ...)` 改為 `if (hasScheduled.processOutbox && ...)`，條件反轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341</code> config 值未驗證型別，可能造成非預期行為</summary>

`config.get('memberWelcomeEmailTestInbox')` 的回傳值可能是任意型別（例如物件或陣列），但程式碼直接將其作為布林值使用。若設定檔中該值為非空字串以外的 truthy 值（如 `{}` 或 `[]`），仍會觸發歡迎郵件邏輯，可能導致非預期行為。

建議明確檢查該值是否為非空字串，或使用 `Boolean()` 轉換並驗證型別。

**判斷依據**：diff 中新增 `const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox');` 並在條件中使用，未見型別驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:340</code> [R20] 使用 var 宣告變數</summary>

此處將原本的 `let member;` 改為 `var member;`，違反專案規範 R20（應使用 let 或 const）。建議改回 `let member;`。

**判斷依據**：diff 中此行由 `let member;` 改為 `var member;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/member-welcome-emails.test.js:53</code> 測試中設定空字串可能無法模擬未設定狀態</summary>

在測試 `does NOT create outbox entry when config is not set` 中，使用 `configUtils.set('memberWelcomeEmailTestInbox', '')` 來模擬未設定。但若實際 config 未設定時回傳 `undefined`，而空字串在條件判斷中也是 falsy，兩者行為相同，因此測試可能無法區分「未設定」與「設定為空字串」。建議使用 `configUtils.set('memberWelcomeEmailTestInbox', undefined)` 或直接刪除該設定，以更貼近實際情境。

**判斷依據**：diff 中此行將原本的 `sinon.stub(labs, 'isSet').withArgs('welcomeEmails').returns(false);` 改為 `configUtils.set('memberWelcomeEmailTestInbox', '');`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6540 (cache hit 4224) ｜ completion tokens 1056 ｜ PR #6</sub>