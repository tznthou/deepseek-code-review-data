<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將網域暖機的郵件量計算從「依前次發送量乘上倍率」改為「依距首封郵件的天數做指數成長」。主要風險在於 `#getDaysSinceFirstEmail` 的日期計算方式、`getWarmupLimit` 回傳 `Infinity` 對呼叫端的影響，以及測試中對天數與數值的假設可能不穩定。建議先確認呼叫端是否能處理 `Infinity`，並修正日期計算的時區與浮點數問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | `getWarmupLimit` 可能回傳 `Infinity`，呼叫端需能處理 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 日期計算可能因時區或浮點數誤差導致天數不正確 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:93` | 指數成長公式在 `totalDays` 為 1 時會除以零 | 0.60 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:239` | 測試中硬編碼的期望值可能因浮點數捨入而脆弱 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> `getWarmupLimit` 可能回傳 `Infinity`，呼叫端需能處理</summary>

當 `day > totalDays` 時，函式回傳 `Infinity`。若呼叫端未預期此值，可能導致後續計算（如 `Math.min`、陣列 slice 等）出現非預期行為。建議確認所有呼叫端都能正確處理 `Infinity`，或改回傳一個明確的哨兵值（例如 `emailCount` 或 `Number.MAX_SAFE_INTEGER`）。

**判斷依據**：diff 中新增的 `getWarmupLimit` 方法在 `day > totalDays` 時回傳 `Infinity`，而舊版實作回傳 `Math.min(emailCount, ...)`，不會有 `Infinity`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 日期計算可能因時區或浮點數誤差導致天數不正確</summary>

`#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `new Date(created_at).getTime()` 的差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或 `created_at` 包含時間部分，可能導致天數計算與預期不符。此外，浮點數除法後取 ceil 可能因精度問題造成邊界錯誤。建議改用 UTC 日期字串比較或明確指定時區。

**判斷依據**：diff 中新增的 `#getDaysSinceFirstEmail` 方法直接使用毫秒差值除以一天毫秒數，未考慮時區或 DST。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:93</code> 指數成長公式在 `totalDays` 為 1 時會除以零</summary>

公式 `day / (this.#warmupConfig.totalDays - 1)` 在 `totalDays` 為 1 時會產生除以零的錯誤。目前預設值為 42，但若未來允許設定，需防範此狀況。

**判斷依據**：diff 中新增的計算式直接使用 `totalDays - 1` 作為分母，未檢查是否為零。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:239</code> 測試中硬編碼的期望值可能因浮點數捨入而脆弱</summary>

測試中直接寫死 `237`、`280` 等數值，但實際計算使用 `Math.floor`，若浮點數運算結果略有不同（例如 236.999999），測試可能失敗。建議使用近似比較或由公式計算期望值。

**判斷依據**：diff 中測試斷言使用精確數值，而實作使用 `Math.floor` 與浮點指數運算。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7591 (cache hit 7552) ｜ completion tokens 1103 ｜ PR #9</sub>