<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 DomainWarmingService 的暖身邏輯從基於前次發送量的倍增表，改為基於首次發送後經過天數的指數成長公式。主要風險在於 `#getDaysSinceFirstEmail` 的日期計算可能因時區或時鐘偏移而產生 off-by-one 錯誤，且 `getWarmupLimit` 在暖身完成後回傳 `Infinity` 可能導致呼叫端未預期的行為。測試已同步更新，但部分測試的期望值與實作公式的捨入方式不一致，可能導致測試不穩定。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 日期計算可能因時區或時鐘偏移產生 off-by-one 錯誤 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | 暖身完成後回傳 Infinity 可能導致呼叫端未預期行為 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:277` | 測試期望值與實作公式的捨入方式不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 日期計算可能因時區或時鐘偏移產生 off-by-one 錯誤</summary>

`#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並無條件進位。若伺服器時區與 UTC 有偏移，或系統時鐘在兩次呼叫間被調整，可能導致天數計算錯誤。例如，若首次 email 建立於 UTC 23:59，而目前時間為 UTC 00:01（相差 2 分鐘），計算結果為 1 天，但實際上可能尚未滿 24 小時。建議改用日曆日期（如 `created_at` 的日期部分與今天的日期差）來計算天數，或明確指定時區。

**判斷依據**：diff 中新增的 `#getDaysSinceFirstEmail` 方法使用毫秒差除以 86400000 並無條件進位，未考慮時區或時鐘偏移。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> 暖身完成後回傳 Infinity 可能導致呼叫端未預期行為</summary>

`getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接使用此值進行數學運算或與其他數值比較，可能產生非預期結果。例如，若呼叫端將此值傳入 `Math.min` 或作為陣列索引，可能導致錯誤。建議回傳 `emailCount`（表示無限制）或定義明確的常數，並確認所有呼叫端都能正確處理。

**判斷依據**：diff 中新增的 `getWarmupLimit` 在暖身完成後回傳 `Infinity`，未見呼叫端處理此特殊值的邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:277</code> 測試期望值與實作公式的捨入方式不一致</summary>

測試中 `getExpectedLimit` 使用 `Math.round`，但實作使用 `Math.floor`。例如 day=1 時，實作計算 `Math.floor(200 * Math.pow(1000, 1/41))` 約為 237，而測試期望值為 237（使用 round 也得到 237），但某些天數可能因捨入差異導致測試失敗。建議測試直接使用與實作相同的公式或驗證範圍而非精確值。

**判斷依據**：diff 中測試的 `getExpectedLimit` 使用 `Math.round`，而服務實作使用 `Math.floor`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9900 (cache hit 9856) ｜ completion tokens 982 ｜ PR #9</sub>