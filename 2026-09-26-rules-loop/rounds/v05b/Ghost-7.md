<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個服務檔案重新命名為 kebab-case，並更新所有 require/import 路徑。整體而言是機械性的重構，風險低，但需注意 macOS/Windows 檔案系統大小寫不敏感可能導致的問題，以及部分檔案在重新命名時混入了非預期的格式變更（如移除分號、調整縮排）。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | [R19] 重新命名時移除了多行結尾分號 | 0.90 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | [R17] 重新命名時縮排從 4 空格變為 0 空格 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | 重新命名時混入非預期的格式變更 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/audience-feedback/audience-feedback-controller.js:77` | 重新命名時移除了行尾空白 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/member-welcome-emails/service.js:103` | 重新命名時移除了多餘空白行 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/stats/posts-stats-service.js:151` | 重新命名時移除了多餘空白行 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/stats/posts-stats-service.js:1571` | 重新命名時新增了檔案結尾換行 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/outbox/index.js:43` | 重新命名時新增了檔案結尾換行 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/outbox/jobs/outbox-job.js:36` | 重新命名時新增了檔案結尾換行 | 0.60 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/outbox/index.test.js:52` | 重新命名時新增了檔案結尾換行 | 0.60 |

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> [R19] 重新命名時移除了多行結尾分號</summary>

在將 `members-api.js` 的 require 路徑改為 kebab-case 的同時，多行原本以分號結尾的陳述式被移除了分號（例如 `const {Router} = require('express')`）。這違反了 repo 規範 R19（必須使用分號），且與本次重新命名的目的無關，可能是編輯器或格式化工具誤操作。建議恢復所有被移除的分號。

**判斷依據**：diff 中 `-const {Router} = require('express');` 變為 `+const {Router} = require('express')`，後續多行也有相同情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> [R17] 重新命名時縮排從 4 空格變為 0 空格</summary>

在 `members-api.js` 的 require 區塊中，原本的 4 空格縮排被移除，導致頂層陳述式沒有縮排。這違反了 repo 規範 R17（4 空格縮排），且與重新命名無關。建議恢復原本的縮排。

**判斷依據**：diff 中 `-const {Router} = require('express');` 變為 `+const {Router} = require('express')`，且行首沒有空格，而其他 require 行仍保留縮排。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> 重新命名時混入非預期的格式變更</summary>

此檔案除了路徑更新外，還包含了移除分號、移除縮排等格式變更，這些變更與 PR 主旨（重新命名為 kebab-case）無關，可能造成 review 噪音。建議將這些格式變更分離到獨立的 commit 或 PR，以維持變更的單一職責。

**判斷依據**：diff 中除了 require 路徑變更外，還有多行分號被移除、縮排被移除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/audience-feedback/audience-feedback-controller.js:77</code> 重新命名時移除了行尾空白</summary>

在 `audience-feedback-controller.js` 中，兩行原本有行尾空白的程式碼被移除了行尾空白（`memberId: member.id, ` → `memberId: member.id,`）。這雖然是好的清理，但與重新命名無關，可能造成不必要的 diff。建議確認是否為有意為之。

**判斷依據**：diff 中 `-            memberId: member.id, ` 變為 `+            memberId: member.id,`，行尾空白被移除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/member-welcome-emails/service.js:103</code> 重新命名時移除了多餘空白行</summary>

在 `member-welcome-emails/service.js` 中，有兩處多餘的空白行被移除（例如 `-        ` 變為 `+`）。這與重新命名無關，但屬於合理的清理。建議確認是否為有意為之。

**判斷依據**：diff 中 `-        ` 變為 `+`，以及 `-            ` 變為 `+`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/stats/posts-stats-service.js:151</code> 重新命名時移除了多餘空白行</summary>

在 `posts-stats-service.js` 中，多處多餘的空白行被移除（例如 `-                            ` 變為 `+`）。這與重新命名無關，但屬於合理的清理。建議確認是否為有意為之。

**判斷依據**：diff 中多處 `-                            ` 變為 `+`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/stats/posts-stats-service.js:1571</code> 重新命名時新增了檔案結尾換行</summary>

在 `posts-stats-service.js` 的結尾，原本沒有換行符號，現在新增了換行符號（`\ No newline at end of file` 被移除）。這與重新命名無關，但屬於合理的清理。建議確認是否為有意為之。

**判斷依據**：diff 中 `-module.exports = PostsStatsService;\ No newline at end of file` 變為 `+module.exports = PostsStatsService;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/outbox/index.js:43</code> 重新命名時新增了檔案結尾換行</summary>

在 `outbox/index.js` 的結尾，原本沒有換行符號，現在新增了換行符號。這與重新命名無關，但屬於合理的清理。建議確認是否為有意為之。

**判斷依據**：diff 中 `-module.exports = new OutboxServiceWrapper();\ No newline at end of file` 變為 `+module.exports = new OutboxServiceWrapper();`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/outbox/jobs/outbox-job.js:36</code> 重新命名時新增了檔案結尾換行</summary>

在 `outbox-job.js` 的結尾，原本沒有換行符號，現在新增了換行符號。這與重新命名無關，但屬於合理的清理。建議確認是否為有意為之。

**判斷依據**：diff 中 `-})();\ No newline at end of file` 變為 `+})();`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/outbox/index.test.js:52</code> 重新命名時新增了檔案結尾換行</summary>

在 `outbox/index.test.js` 的結尾，原本沒有換行符號，現在新增了換行符號。這與重新命名無關，但屬於合理的清理。建議確認是否為有意為之。

**判斷依據**：diff 中 `-});\ No newline at end of file` 變為 `+});`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 48966 (cache hit 48896) ｜ completion tokens 2152 ｜ PR #7</sub>