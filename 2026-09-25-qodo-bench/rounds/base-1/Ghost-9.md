<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Domain Warming 的郵件量計算從「依前次最高寄送量乘上倍率」改為「依距離第一封郵件的天數做指數成長」。整體方向合理，但實作上存在幾個需要修正的問題：最嚴重的是 `getWarmupLimit` 在暖機完成後回傳 `Infinity`，這會讓呼叫端在 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未做防護，可能導致非預期行為；此外，天數計算使用 `Date.now()` 而非注入的時鐘，在測試中可能因時區或時間差導致 flaky；最後，`#getDaysSinceFirstEmail` 的查詢條件 `csd_email_count:-null` 可能無法正確過濾出 null 值，且未處理 `created_at` 為 null 的情況。建議優先修正 Infinity 回傳與時間相依性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | 暖機完成後回傳 Infinity 可能導致非預期行為 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 天數計算使用 Date.now() 導致測試不穩定 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:66` | 查詢條件 csd_email_count:-null 可能無法正確過濾 null | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 未處理 created_at 為 null 的情況 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> 暖機完成後回傳 Infinity 可能導致非預期行為</summary>

在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

**判斷依據**：diff 中新增的程式碼片段，直接回傳 `Infinity`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 天數計算使用 Date.now() 導致測試不穩定</summary>

`#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

**判斷依據**：diff 中新增的程式碼片段，使用 `Date.now()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:66</code> 查詢條件 csd_email_count:-null 可能無法正確過濾 null</summary>

`#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

**判斷依據**：diff 中新增的查詢條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 未處理 created_at 為 null 的情況</summary>

`#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

**判斷依據**：diff 中新增的程式碼片段，未對 `created_at` 進行 null 或格式檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7591 (cache hit 1536) ｜ completion tokens 1178 ｜ PR #9</sub>