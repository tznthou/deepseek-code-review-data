<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 將 DomainWarmingService 的暖身邏輯從基於上次發送量的倍率表改為基於時間的指數成長公式。改動本身未違反任何 repo 規範，但測試檔案中出現多處違反 R19（缺少分號）與 R18（使用雙引號）的程式碼，應在合併前修正以維持程式碼風格一致性。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:84` | [R19] 缺少分號 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:89` | [R19] 缺少分號 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:97` | [R19] 缺少分號 | 0.95 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:201` | [R19] 缺少分號 | 0.95 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:203` | [R19] 缺少分號 | 0.95 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:315` | [R19] 缺少分號 | 0.95 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:316` | [R19] 缺少分號 | 0.95 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:112` | [R18] 使用雙引號 | 0.95 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:113` | [R18] 使用雙引號 | 0.95 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:114` | [R18] 使用雙引號 | 0.95 |

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:84</code> [R19] 缺少分號</summary>

在 `getWarmupLimit` 方法中，`const day = await this.#getDaysSinceFirstEmail()` 與 `return Infinity` 兩行結尾缺少分號，違反 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號，與專案規範 R19 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:89</code> [R19] 缺少分號</summary>

`const limit = Math.floor(...)` 陳述句結尾缺少分號，違反 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號，與專案規範 R19 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:97</code> [R19] 缺少分號</summary>

`return Math.min(emailCount, limit)` 陳述句結尾缺少分號，違反 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號，與專案規範 R19 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:201</code> [R19] 缺少分號</summary>

`const expectedLimit = Math.min(email2Count, 237);` 這一行結尾缺少分號，違反 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號，與專案規範 R19 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:203</code> [R19] 缺少分號</summary>

`assert.equal(csdCount2, expectedLimit, 'Day 2 should use time-based warmup limit');` 這一行結尾缺少分號，違反 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號，與專案規範 R19 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:315</code> [R19] 缺少分號</summary>

`const expectedLimit = Math.min(totalCount, getExpectedLimit(day));` 這一行結尾缺少分號，違反 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號，與專案規範 R19 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:316</code> [R19] 缺少分號</summary>

`assert.equal(csdCount, expectedLimit, `Day ${day}: Should match time-based warmup limit`);` 這一行結尾缺少分號，違反 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號，與專案規範 R19 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:112</code> [R18] 使用雙引號</summary>

`const date = new Date('2024-01-15T12:00:00Z');` 使用雙引號包覆字串，違反 R18（應使用單引號）。

**判斷依據**：diff 中新增的程式碼使用雙引號，與專案規範 R18 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:113</code> [R18] 使用雙引號</summary>

`date.setDate(date.getDate() - days);` 使用雙引號包覆字串，違反 R18（應使用單引號）。

**判斷依據**：diff 中新增的程式碼使用雙引號，與專案規範 R18 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:114</code> [R18] 使用雙引號</summary>

`return date.toISOString();` 使用雙引號包覆字串，違反 R18（應使用單引號）。

**判斷依據**：diff 中新增的程式碼使用雙引號，與專案規範 R18 衝突。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9937 (cache hit 9856) ｜ completion tokens 1774 ｜ PR #9</sub>