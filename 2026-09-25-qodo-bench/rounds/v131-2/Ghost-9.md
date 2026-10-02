<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Domain Warming 的郵件量計算從基於歷史最高發送量的分段縮放表，改為基於首次發送後經過天數的指數成長公式。整體方向合理，但存在幾個關鍵問題：1) `#getDaysSinceFirstEmail` 使用 `Math.ceil` 計算天數，導致第一天（day 0）被算成 day 1，造成暖機進度提前一天；2) 當暖機完成後回傳 `Infinity`，可能導致呼叫端未預期的行為（例如嘗試發送無限封郵件）；3) 測試中使用了 `Math.round` 而非實作中的 `Math.floor`，可能造成測試與實作不一致；4) 缺少對 `created_at` 無效值的處理。建議優先修正天數計算與 `Infinity` 回傳值的設計。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 天數計算使用 Math.ceil 導致暖機進度提前一天 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | 暖機完成後回傳 Infinity 可能導致呼叫端錯誤 | 0.85 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:302` | 測試使用 Math.round 與實作 Math.floor 不一致 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 未處理 created_at 無效或缺失的情況 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 天數計算使用 Math.ceil 導致暖機進度提前一天</summary>

`#getDaysSinceFirstEmail` 使用 `Math.ceil` 將毫秒差轉換為天數。這會導致在第一天（距離首次發送不到 24 小時）時，計算出的天數為 1 而非 0。例如，若首次發送在 1 月 1 日 12:00，而當前時間為 1 月 1 日 13:00，則 `Math.ceil(1小時 / 24小時) = 1`，使得暖機公式使用 day=1 的指數值，而非 day=0 的起始值。這會讓暖機進度提前一天，可能導致發送量過高。建議改用 `Math.floor` 或直接計算整天數（例如 `Math.floor((Date.now() - firstEmailTime) / (1000 * 60 * 60 * 24))`）。

**判斷依據**：diff 中新增的 `#getDaysSinceFirstEmail` 方法，使用 `Math.ceil` 計算天數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> 暖機完成後回傳 Infinity 可能導致呼叫端錯誤</summary>

當 `day > totalDays` 時，`getWarmupLimit` 回傳 `Infinity`。這可能導致呼叫端在未預期的情況下嘗試發送無限封郵件，或將 `Infinity` 傳遞給其他函式造成錯誤。建議改為回傳 `emailCount`（表示暖機完成，全部使用自訂網域發送），或明確回傳一個有限值，並在文件或型別中說明。

**判斷依據**：diff 中新增的 `getWarmupLimit` 方法，在 `day > totalDays` 時回傳 `Infinity`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:302</code> 測試使用 Math.round 與實作 Math.floor 不一致</summary>

在整合測試中，`getExpectedLimit` 使用 `Math.round` 計算期望值，但實作中使用 `Math.floor`。這可能導致測試在某些天數下期望值與實作不同，造成測試不穩定或錯誤。建議統一使用 `Math.floor` 或直接複製實作邏輯。

**判斷依據**：diff 中測試程式碼新增的 `getExpectedLimit` 函式使用 `Math.round`，而實作在 `DomainWarmingService.ts` 中使用 `Math.floor`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 未處理 created_at 無效或缺失的情況</summary>

`#getDaysSinceFirstEmail` 直接使用 `new Date(res.data[0].get('created_at') as string).getTime()`，若 `created_at` 為 null、undefined 或無效字串，會導致 `NaN`，進而使天數計算錯誤。建議加入防禦性檢查，例如若無法取得有效日期則回傳 0。

**判斷依據**：diff 中新增的 `#getDaysSinceFirstEmail` 方法，未對 `created_at` 進行有效性驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7555 (cache hit 7552) ｜ completion tokens 1281 ｜ PR #9</sub>