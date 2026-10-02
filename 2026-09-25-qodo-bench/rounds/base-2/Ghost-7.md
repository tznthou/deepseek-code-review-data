<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量服務檔案重新命名為 kebab-case，並更新所有 require/import 路徑。整體為機械式重構，風險低，但需注意 macOS/Windows 檔案系統大小寫不敏感可能導致的路徑解析問題，以及部分檔案中混雜的格式調整。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | require 陳述式移除分號 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:9` | require 路徑大小寫變更可能導致 macOS/Windows 解析失敗 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:18` | require 路徑大小寫變更可能導致 macOS/Windows 解析失敗 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:19` | require 路徑大小寫變更可能導致 macOS/Windows 解析失敗 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | require 陳述式移除分號可能違反 ESLint 規則 | 0.50 |

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> require 陳述式移除分號</summary>

此檔案中多個 require 陳述式移除了行尾分號（例如 `const {Router} = require('express')`），與專案其他檔案的風格不一致。若專案有 ESLint 規則強制分號，可能導致 CI 失敗。

**判斷依據**：diff 中可見原本有分號的 require 被改為無分號，但其他檔案仍保留分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:9</code> require 路徑大小寫變更可能導致 macOS/Windows 解析失敗</summary>

路徑從 `./services/MemberBREADService` 改為 `./services/member-bread-service`，但實際檔案名稱已改為 `member-bread-service.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

**判斷依據**：diff 中可見路徑變更，且檔案重新命名為小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:18</code> require 路徑大小寫變更可能導致 macOS/Windows 解析失敗</summary>

路徑從 `../../email-suppression-list/EmailSuppressionList` 改為 `../../email-suppression-list/email-suppression-list`，但實際檔案名稱已改為 `email-suppression-list.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

**判斷依據**：diff 中可見路徑變更，且檔案重新命名為小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:19</code> require 路徑大小寫變更可能導致 macOS/Windows 解析失敗</summary>

路徑從 `../../lib/magic-link/MagicLink` 改為 `../../lib/magic-link/magic-link`，但實際檔案名稱已改為 `magic-link.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

**判斷依據**：diff 中可見路徑變更，且檔案重新命名為小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> require 陳述式移除分號可能違反 ESLint 規則</summary>

此檔案中多個 require 陳述式移除了行尾分號，若專案使用 ESLint 的 `semi` 規則，可能導致 lint 失敗。

**判斷依據**：diff 中可見原本有分號的 require 被改為無分號。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 46733 (cache hit 46720) ｜ completion tokens 1105 ｜ PR #7</sub>