<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Domain Warming 的計算方式從「依前次發送量倍增」改為「依時間指數成長」。整體方向合理，但存在一個關鍵的 off-by-one 錯誤：`#getDaysSinceFirstEmail` 使用 `Math.ceil` 計算天數，導致第一天就被視為 day 1，使暖機進度提前一天，且測試中的期望值與實作不一致。此外，`getWarmupLimit` 回傳 `Infinity` 可能造成下游型別或比較上的問題，建議改用明確的哨兵值或直接回傳 `emailCount`。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 天數計算 off-by-one：第一天就被當成 day 1 | 0.95 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:150` | 測試期望值與實作不一致：day 0 應為 200，但實作會回傳 237 | 0.85 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:175` | 測試期望值與實作不一致：day 1 應為 237，但實作會回傳 280 | 0.85 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:262` | 測試期望值與實作不一致：day 41 應為 200000，但實作會回傳 Infinity | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | 回傳 `Infinity` 可能造成下游型別或比較問題 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 天數計算 off-by-one：第一天就被當成 day 1</summary>

`#getDaysSinceFirstEmail` 使用 `Math.ceil` 計算經過天數，導致在暖機開始當天（day 0）就會得到 day 1。這會使暖機進度提前一天，例如在第一天就套用 day 1 的 limit（237），而不是 day 0 的 200。

**失敗情境**：
- 使用者在 2024-01-15 12:00 建立第一封 email，並在 2024-01-15 13:00 呼叫 `getWarmupLimit`。
- `#getDaysSinceFirstEmail` 會計算 `(Date.now() - firstEmailTime) / (1000*60*60*24)` ≈ 0.0417，`Math.ceil` 後得到 1。
- `getWarmupLimit` 會回傳 day 1 的 limit（237），而不是 day 0 的 200。

**建議修法**：
改用 `Math.floor` 來計算天數，讓 day 0 代表第一天。

**判斷依據**：diff 中新增的 `#getDaysSinceFirstEmail` 方法使用 `Math.ceil`，而測試中 `daysAgo(0)` 的期望值是 200（day 0），但實際會得到 day 1 的 237。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:150</code> 測試期望值與實作不一致：day 0 應為 200，但實作會回傳 237</summary>

在 `should return 200 (start value) when first email was today (day 0)` 測試中，`created_at` 設為 `daysAgo(0)`，期望回傳 200。但由於 `#getDaysSinceFirstEmail` 使用 `Math.ceil`，實際會得到 day 1，因此 `getWarmupLimit` 會回傳 237，導致測試失敗。

**建議修法**：
修正 `#getDaysSinceFirstEmail` 的 off-by-one 錯誤後，此測試應可通過。

**判斷依據**：測試中 `daysAgo(0)` 對應到 day 0，但實作會將當天視為 day 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:175</code> 測試期望值與實作不一致：day 1 應為 237，但實作會回傳 280</summary>

在 `should return calculated limit when emailCount is greater` 測試中，`created_at` 設為 `daysAgo(1)`，期望回傳 237。但由於 `#getDaysSinceFirstEmail` 使用 `Math.ceil`，實際會得到 day 2（因為 day 1 的 0.0417 被進位成 1，再 +1？），因此 `getWarmupLimit` 會回傳 day 2 的 limit（280），導致測試失敗。

**建議修法**：
修正 `#getDaysSinceFirstEmail` 的 off-by-one 錯誤後，此測試應可通過。

**判斷依據**：測試中 `daysAgo(1)` 對應到 day 1，但實作會將前一天視為 day 2。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:262</code> 測試期望值與實作不一致：day 41 應為 200000，但實作會回傳 Infinity</summary>

在 `should return correct warmup progression through the days` 測試中，`day: 41` 的期望值是 200000。但由於 `#getDaysSinceFirstEmail` 使用 `Math.ceil`，實際會得到 day 42（因為 day 41 的 0.9583 被進位成 1，再 +41？），因此 `getWarmupLimit` 會回傳 `Infinity`（因為 `day > totalDays`），導致測試失敗。

**建議修法**：
修正 `#getDaysSinceFirstEmail` 的 off-by-one 錯誤後，此測試應可通過。

**判斷依據**：測試中 `day: 41` 對應到 day 41，但實作會將第 41 天視為 day 42，觸發 `Infinity` 回傳。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> 回傳 `Infinity` 可能造成下游型別或比較問題</summary>

當暖機完成後，`getWarmupLimit` 回傳 `Infinity`。這可能導致下游程式碼在進行數值比較或計算時出現非預期行為，例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若下游直接使用該值進行算術運算，可能產生 `Infinity` 或 `NaN`。

**建議修法**：
回傳 `emailCount` 本身，或使用一個明確的哨兵值（例如 `Number.MAX_SAFE_INTEGER`），並在文件或型別中說明。

**判斷依據**：diff 中新增的 `getWarmupLimit` 方法在 `day > totalDays` 時回傳 `Infinity`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10688 (cache hit 1536) ｜ completion tokens 1748 ｜ PR #9</sub>