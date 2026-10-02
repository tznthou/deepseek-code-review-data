<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Domain Warming 的擴充倍率，並將查詢從 findOne 改為 findPage。主要風險在於邊界條件處理：thresholds 的比較從 <= 改為 <，可能導致特定數值（如 1000）落入錯誤的倍率區間；同時高流量（>=400k）的計算邏輯中，scaledIncrease 使用 maxScale 而非 1+maxScale，可能造成成長停滯。測試覆蓋了主要路徑，但需確認邊界值與既有行為的相容性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:132` | threshold 比較運算子從 <= 改為 < 可能造成倍率錯誤 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高流量計算中 scaledIncrease 使用 maxScale 而非 1+maxScale | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:125` | 高流量 threshold 判斷使用 >= 可能包含等於 400000 的情況 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | findPage 查詢的 filter 使用 <= 可能包含當天資料 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:132</code> threshold 比較運算子從 <= 改為 < 可能造成倍率錯誤</summary>

在 `getWarmupLimit` 中，原本使用 `lastCount <= threshold.limit` 來決定倍率，現在改為 `lastCount < threshold.limit`。這會導致當 `lastCount` 恰好等於某個 threshold 的 limit 時，會落入下一個更高的倍率區間。例如 `lastCount = 1000` 時，原本應使用 1.25 倍（因為 <= 1000），現在會使用 1.5 倍（因為 < 1000 不成立，進入下一個 threshold）。這可能造成實際發送量超出預期，影響 warmup 的漸進性。建議改回 `<=` 或明確處理等於邊界的情況。

**判斷依據**：diff 中 `-            if (lastCount <= threshold.limit) {` 改為 `+            if (lastCount < threshold.limit) {`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高流量計算中 scaledIncrease 使用 maxScale 而非 1+maxScale</summary>

在高流量區段（`lastCount >= 400000`）的計算中，`scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale)`，其中 `maxScale` 為 1.2。這表示 scaledIncrease 會是 `lastCount * 1.2`，但註解說明「cap the increase at 20%」，即應為 `lastCount * (1 + 0.2)`。目前程式碼會讓 scaledIncrease 永遠小於 absoluteIncrease（`lastCount + 75000`），因此實際回傳值會是 `lastCount * 1.2`，而非預期的 `lastCount * 1.2` 與 `lastCount + 75000` 的最小值。這可能導致高流量時成長幅度過小，甚至停滯。建議將 `maxScale` 改為 `1 + maxScale` 或調整計算方式。

**判斷依據**：diff 中新增的程式碼，且 `highVolume.maxScale` 定義為 1.2

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:125</code> 高流量 threshold 判斷使用 >= 可能包含等於 400000 的情況</summary>

在高流量判斷中，使用 `lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold`，其中 threshold 為 400000。這表示當 `lastCount` 恰好等於 400000 時，會進入高流量邏輯。然而，在 thresholds 陣列中，最後一個 threshold 的 limit 也是 400000，且其 scale 為 2。原本的邏輯中，`lastCount <= 400000` 會使用 2 倍，但現在等於 400000 會先被高流量邏輯攔截，使用 1.2 倍或 +75k 的規則。這可能造成行為不一致。建議確認是否應使用 `>` 而非 `>=`，或調整 threshold 的 limit 以避免重疊。

**判斷依據**：diff 中新增的程式碼，且 thresholds 最後一項 limit 為 400_000

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> findPage 查詢的 filter 使用 <= 可能包含當天資料</summary>

原本的 `findOne` 使用 `created_at:<${date}`（嚴格小於），現在改為 `created_at:<=${date}`（小於等於）。這表示查詢會包含當天建立的 email，可能導致 `#getHighestCount` 取得今天的資料，進而影響 warmup 計算。若目的是排除今天，應維持 `<`。建議確認此變更是否為預期。

**判斷依據**：diff 中 `-            filter: `created_at:<${new Date().toISOString().split('T')[0]}`,` 改為 `+            filter: `created_at:<=${new Date().toISOString().split('T')[0]}`,

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7453 (cache hit 6144) ｜ completion tokens 1371 ｜ PR #3</sub>