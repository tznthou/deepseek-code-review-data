<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 DomainWarmingService 的暖機擴充邏輯，將原本的倍增策略改為分段乘數，並針對高流量（400k+）設定絕對增量上限。主要風險在於 `#getHighestCount` 改用 `findPage` 後，若 `findPage` 回傳的資料結構與預期不符（例如 `data` 不是陣列或元素缺少 `get` 方法），可能導致執行時期錯誤。此外，測試中對 `findPage` 的模擬方式與實際使用不一致，可能掩蓋真實問題。建議先確認 `findPage` 的契約並補強錯誤處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:101` | findPage 回傳結構假設可能導致執行時期錯誤 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 測試中對 findPage 的模擬與實際使用不一致 | 0.75 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高流量分支的計算可能與預期不符 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:101</code> findPage 回傳結構假設可能導致執行時期錯誤</summary>

`#getHighestCount` 假設 `findPage` 回傳的物件具有 `data` 陣列，且每個元素都有 `get` 方法。若實際回傳結構不同（例如 `data` 為 undefined 或元素為 plain object），則 `result.data.length` 或 `result.data[0].get` 會拋出錯誤。建議加入防禦性檢查，或確認 `findPage` 的型別定義與實際實作一致。

**判斷依據**：diff 中新增的 `findPage` 呼叫與後續對 `result.data` 的存取，但未驗證 `result.data` 是否存在或元素是否具有 `get` 方法。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 測試中對 findPage 的模擬與實際使用不一致</summary>

在 `beforeEach` 中，`Email` 被設定為 `createModelClass({ findAll: [] })`，但服務實際呼叫的是 `findPage`。這可能導致測試在未正確模擬 `findPage` 的情況下執行，掩蓋真實行為。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 會自動將 `findAll` 映射到 `findPage`。

**判斷依據**：diff 中 `beforeEach` 的設定仍使用 `findAll`，但服務程式碼已改用 `findPage`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高流量分支的計算可能與預期不符</summary>

在高流量分支中，`scaledIncrease` 使用 `Math.ceil(lastCount * maxScale)`，而 `absoluteIncrease` 使用 `lastCount + maxAbsoluteIncrease`。若 `lastCount` 很大，`Math.ceil` 可能導致結果比預期多 1，但影響輕微。建議確認此行為是否符合預期。

**判斷依據**：diff 中高流量分支的計算邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8573 (cache hit 1536) ｜ completion tokens 975 ｜ PR #3</sub>