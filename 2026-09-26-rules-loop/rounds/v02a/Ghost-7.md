<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量檔案重新命名為 kebab-case，並更新所有 require/import 路徑。整體而言是機械性的重構，風險低，但需注意幾個可能遺漏的引用、不一致的命名，以及一個檔案中混用了有無分號的風格。建議修正後合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | [R19] 部分 require 陳述式缺少分號 | 0.90 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:9` | 命名不一致：MemberBREADService 改為 member-bread-service | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:19` | 可能遺漏的引用：MagicLink 路徑未更新？ | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:18` | 可能遺漏的引用：EmailSuppressedEvent 路徑未更新？ | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | 檔案開頭缺少分號可能導致 ASI 問題 | 0.60 |

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> [R19] 部分 require 陳述式缺少分號</summary>

在此檔案中，前 10 行的 require 陳述式結尾沒有分號，但後續的 require 陳述式（例如 `const EventRepository = require('./repositories/event-repository');`）卻有分號。這違反了專案規範 R19（必須使用分號），且風格不一致。

**判斷依據**：diff 中新增的這幾行沒有分號，但同一檔案後面的 require 有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:9</code> 命名不一致：MemberBREADService 改為 member-bread-service</summary>

原本的 `MemberBREADService` 被改名為 `member-bread-service`，但 BREAD 是縮寫，通常應保留大寫或轉為 `member-bread-service` 可能造成語意不清。建議確認是否應為 `member-bread-service` 或 `member-bread-service`（若 BREAD 是專有名詞，可能應保留為 `member-bread-service`）。

**判斷依據**：diff 中將 `MemberBREADService` 改為 `member-bread-service`，但其他類似服務如 `PaymentsService` 改為 `payments-service`，此處 BREAD 縮寫的處理可能不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:19</code> 可能遺漏的引用：MagicLink 路徑未更新？</summary>

在 diff 中，`MagicLink` 的 require 路徑從 `../../lib/magic-link/MagicLink` 改為 `../../lib/magic-link/magic-link`，但未看到對應的檔案重新命名。請確認 `ghost/core/core/server/services/lib/magic-link/MagicLink.js` 是否已改名為 `magic-link.js`，否則會導致模組找不到。

**判斷依據**：diff 中只更新了 require 路徑，但沒有顯示 `MagicLink.js` 的 rename。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:18</code> 可能遺漏的引用：EmailSuppressedEvent 路徑未更新？</summary>

在 diff 中，`EmailSuppressedEvent` 的 require 路徑從 `../../email-suppression-list/EmailSuppressionList` 改為 `../../email-suppression-list/email-suppression-list`，但未看到對應的檔案重新命名。請確認 `EmailSuppressionList.js` 是否已改名為 `email-suppression-list.js`，否則會導致模組找不到。

**判斷依據**：diff 中只更新了 require 路徑，但沒有顯示 `EmailSuppressionList.js` 的 rename。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> 檔案開頭缺少分號可能導致 ASI 問題</summary>

雖然缺少分號通常不會造成立即錯誤，但根據專案規範 R19，所有陳述式都應以分號結尾。建議補上分號以維持一致性。

**判斷依據**：diff 中新增的這一行沒有分號。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 49042 (cache hit 1536) ｜ completion tokens 1251 ｜ PR #7</sub>