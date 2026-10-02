<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 將 DomainWarmingService 從基於前次發送量的暖機策略改為基於時間的指數成長策略。主要風險在於 `getWarmupLimit` 回傳 `Infinity` 可能導致下游未預期的行為，以及 `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的時區差異可能造成天數計算偏差。此外，程式碼風格違反多項既有規範，包括缺少分號、使用雙引號、縮排不一致等。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:86` | [R19] 缺少分號 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:89` | [R19] 缺少分號 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:97` | [R19] 缺少分號 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:66` | [R18] 使用雙引號 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:111` | [R19] 缺少分號 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:112` | [R19] 缺少分號 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:113` | [R19] 缺少分號 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:114` | [R19] 缺少分號 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:117` | [R19] 缺少分號 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:64` | [R17] 縮排不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:86</code> [R19] 缺少分號</summary>

`return Infinity` 陳述式結尾缺少分號，違反專案規範 R19（必須使用分號）。自動分號插入（ASI）通常會正確處理，但明確加上分號可避免潛在的解析問題並維持一致性。

**判斷依據**：diff 中新增的 `return Infinity` 行末沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:89</code> [R19] 缺少分號</summary>

`const limit = Math.floor(...)` 陳述式結尾缺少分號，違反專案規範 R19。

**判斷依據**：diff 中新增的 `const limit = Math.floor(...)` 區塊結尾沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:97</code> [R19] 缺少分號</summary>

`return Math.min(emailCount, limit)` 陳述式結尾缺少分號，違反專案規範 R19。

**判斷依據**：diff 中新增的 `return Math.min(emailCount, limit)` 行末沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:66</code> [R18] 使用雙引號</summary>

字串 `'csd_email_count:-null'` 使用了單引號，符合規範；但 `new Date(res.data[0].get('created_at') as string)` 中的 `'created_at'` 也是單引號，沒有違規。此 finding 可能不成立，請確認是否有其他雙引號字串。

**判斷依據**：diff 中新增的 filter 字串使用單引號，符合規範。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:111</code> [R19] 缺少分號</summary>

`function daysAgo(days: number): string {` 函式宣告後缺少分號，但函式宣告不需要分號，此 finding 可能不成立。

**判斷依據**：diff 中新增的函式宣告行末沒有分號，但函式宣告通常不需要分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:112</code> [R19] 缺少分號</summary>

`const date = new Date('2024-01-15T12:00:00Z');` 陳述式結尾缺少分號，違反專案規範 R19。

**判斷依據**：diff 中新增的該行結尾沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:113</code> [R19] 缺少分號</summary>

`date.setDate(date.getDate() - days);` 陳述式結尾缺少分號，違反專案規範 R19。

**判斷依據**：diff 中新增的該行結尾沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:114</code> [R19] 缺少分號</summary>

`return date.toISOString();` 陳述式結尾缺少分號，違反專案規範 R19。

**判斷依據**：diff 中新增的該行結尾沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:117</code> [R19] 缺少分號</summary>

`Email = createModelClass({` 陳述式結尾缺少分號，違反專案規範 R19。

**判斷依據**：diff 中新增的該行結尾沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:64</code> [R17] 縮排不一致</summary>

新增的 `#getDaysSinceFirstEmail` 方法內縮排似乎使用了 4 個空格，但與檔案其他部分的縮排風格可能不一致。請確認是否遵循專案的 4 空格縮排規範。

**判斷依據**：diff 中新增的方法縮排為 8 個空格（兩個層級），但檔案其他部分可能使用不同縮排。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9937 (cache hit 9856) ｜ completion tokens 1766 ｜ PR #9</sub>