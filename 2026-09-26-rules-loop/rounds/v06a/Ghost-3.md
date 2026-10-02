<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 調整了 Domain Warming 的擴充倍率，從原本的 2 倍改為較保守的 1.25 倍起跳，並新增高量寄送者的上限機制。主要風險在於 `getWarmupLimit` 的邊界條件處理：`lastCount` 等於 400,000 時會落入高量區塊，但測試案例卻預期使用 2 倍，顯示程式碼與測試不一致。此外，`findPage` 的 filter 從 `<` 改為 `<=` 可能納入當日資料，影響基準值。建議先修正邊界條件與測試，並確認 filter 語義。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:125` | 高量寄送者邊界條件錯誤：lastCount = 400,000 時應使用 2 倍而非高量上限 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | filter 從 `<` 改為 `<=` 可能納入當日資料，影響基準值 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:181` | 測試斷言仍使用舊的 `<` 運算子，與實作不一致 | 0.80 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:183` | 測試斷言未檢查 limit 參數，可能遺漏回歸 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:125</code> 高量寄送者邊界條件錯誤：lastCount = 400,000 時應使用 2 倍而非高量上限</summary>

在 `getWarmupLimit` 中，高量區塊的條件是 `lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold`，其中 threshold 為 400,000。因此當 `lastCount` 恰好等於 400,000 時，會進入高量區塊，回傳 `min(400000 * 1.2, 400000 + 75000) = min(480000, 475000) = 475000`。然而，單元測試 `should return correct warmup progression through the stages` 中，測試案例 `{lastCount: 400000, expected: 800000}` 預期回傳 800,000（即 2 倍）。這表示程式碼與測試不一致，且根據註解中的倍率表，400,000 應屬於 2 倍區間（100k–400k），因此高量區塊的條件應改為 `>` 而非 `>=`。

**判斷依據**：diff 中新增的條件 `if (lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold)` 與測試案例 `{lastCount: 400000, expected: 800000}` 衝突。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> filter 從 `<` 改為 `<=` 可能納入當日資料，影響基準值</summary>

原本的 filter 使用 `created_at:<${today}` 排除當日建立的郵件，但修改後改為 `created_at:<=${today}`，這會將當日建立的郵件也納入最高計數的計算。這可能導致基準值被當日寄送量影響，進而高估暖機限制。若意圖是排除當日，應維持 `<`；若意圖是包含當日，則需確認此變更的合理性，並更新相關測試。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:181</code> 測試斷言仍使用舊的 `<` 運算子，與實作不一致</summary>

在測試 `should query for emails created before today` 中，斷言 `callArgs.filter.includes(`created_at:<${today}`)` 仍檢查 `<`，但實作已改為 `<=`。這會導致測試失敗，且無法驗證新的 filter 行為。應更新斷言以匹配實作，或根據預期行為調整實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:183</code> 測試斷言未檢查 limit 參數，可能遺漏回歸</summary>

測試 `should query for emails created before today` 中，新增了 `assert.equal(callArgs.limit, 1)`，但未驗證 `findPage` 是否被正確呼叫。若未來 `findPage` 的呼叫方式變更，此測試可能無法捕捉到問題。建議增加對 `findPage` 呼叫次數與參數的完整驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8563 (cache hit 6144) ｜ completion tokens 1167 ｜ PR #3</sub>