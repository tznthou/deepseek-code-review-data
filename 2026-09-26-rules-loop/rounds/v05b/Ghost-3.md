<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 DomainWarmingService 的擴展因子，並將查詢從 findOne 改為 findPage。主要風險在於查詢條件從 `<` 改為 `<=` 可能導致重複計算當日最高值，以及高量級（400k+）的計算邏輯可能造成非預期的成長上限。測試已更新以反映新邏輯，但需確認查詢條件變更的意圖。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | 查詢條件從 `<` 改為 `<=` 可能包含當日最高值，導致重複計算 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高量級（400k+）的計算邏輯可能造成非預期的成長上限 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 測試中 Email 模型建立方式不一致 | 0.60 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:54` | 測試中 `baseDate` 使用 `new Date()` 可能導致跨日不穩定 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> 查詢條件從 `<` 改為 `<=` 可能包含當日最高值，導致重複計算</summary>

原本使用 `created_at:<today` 排除當日，現在改為 `created_at:<=today` 會包含當日建立的 email。若當日已寄出多封 email，`#getHighestCount()` 會取得當日最高值，可能造成暖機限制計算錯誤（例如當日已達上限，隔日計算時會以當日最高值為基礎，而非昨日最高值）。建議確認此變更是否為預期行為，或改回 `<`。

**判斷依據**：diff 中將 `created_at:<` 改為 `created_at:<=`，且註解仍寫「excluding today」，但實際查詢包含當日。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高量級（400k+）的計算邏輯可能造成非預期的成長上限</summary>

在 `lastCount >= 400000` 時，回傳 `Math.min(lastCount * 1.2, lastCount + 75000)`。但若 `lastCount` 極大（例如 1,000,000），`lastCount + 75000` 會小於 `lastCount * 1.2`，導致成長上限僅為 75k，可能過於保守。請確認此設計是否符合預期，或考慮使用 `Math.min(lastCount * 1.2, lastCount + maxAbsoluteIncrease)` 但調整 `maxAbsoluteIncrease` 的數值。

**判斷依據**：diff 中新增的 highVolume 邏輯，且測試案例 `{lastCount: 800000, expected: 875000}` 顯示 800k + 75k = 875k，但 800k * 1.2 = 960k，因此取 875k。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 測試中 Email 模型建立方式不一致</summary>

在 `beforeEach` 中，`Email = createModelClass({ findAll: [] })`，但在某些測試中又覆寫為 `createModelClass({ findAll: [{...}] })`。這可能導致測試之間的狀態污染，建議統一使用 `sinon.stub()` 或確保每個測試獨立建立模型。

**判斷依據**：diff 中將原本的 `findOne: null` 改為 `findAll: []`，但後續測試仍使用 `createModelClass` 並傳入不同資料。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:54</code> 測試中 `baseDate` 使用 `new Date()` 可能導致跨日不穩定</summary>

`baseDate` 在測試檔案載入時建立，若測試執行跨過午夜，`setDay` 的基準日期可能不正確。建議使用固定日期（例如 `new Date('2025-01-01T12:00:00')`）以確保測試可重現。

**判斷依據**：diff 中新增的 `baseDate` 使用當前時間，可能因執行時間不同而影響測試結果。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8497 (cache hit 8448) ｜ completion tokens 1170 ｜ PR #3</sub>