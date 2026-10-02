<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量服務檔案重新命名為 kebab-case，並更新所有相關的 require/import 路徑。整體而言，這是一次大規模的機械式重構，風險主要在於是否有遺漏的引用或大小寫敏感檔案系統上的問題。此外，部分檔案在重新命名時也順帶調整了程式碼格式（如移除行尾空白、修正縮排），但未見功能性變更。建議合併前確認 CI 測試全數通過，並留意是否有其他未涵蓋的引用。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | [R19] 部分 require 陳述式缺少分號 | 0.90 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:12` | [R19] 部分 require 陳述式缺少分號 | 0.90 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:18` | [R19] 部分 require 陳述式缺少分號 | 0.90 |

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> [R19] 部分 require 陳述式缺少分號</summary>

在此檔案的重新命名過程中，部分 require 陳述式結尾的分號被移除（例如 `const {Router} = require('express')`、`const body = require('body-parser')` 等），違反了專案規範 R19（所有陳述式必須以分號結尾）。建議補回分號以維持一致性。

**判斷依據**：diff 中顯示原本有分號的 require 陳述式在修改後被移除分號，例如 `-const {Router} = require('express');` 變成 `+const {Router} = require('express')`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:12</code> [R19] 部分 require 陳述式缺少分號</summary>

此處的 `const EventRepository = require('./repositories/event-repository');` 等行保留了分號，但同一檔案中其他 require 陳述式卻沒有分號，造成不一致。建議統一加上分號。

**判斷依據**：diff 中顯示這些行在修改後仍保留分號，但與上方缺少分號的 require 陳述式形成對比。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:18</code> [R19] 部分 require 陳述式缺少分號</summary>

`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list');` 和 `const MagicLink = require('../../lib/magic-link/magic-link');` 這兩行保留了分號，但與檔案中其他缺少分號的 require 陳述式不一致。建議統一加上分號。

**判斷依據**：diff 中顯示這兩行在修改後仍保留分號，但與上方缺少分號的 require 陳述式形成對比。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 49042 (cache hit 49024) ｜ completion tokens 955 ｜ PR #7</sub>