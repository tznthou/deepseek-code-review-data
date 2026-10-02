<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 調整了 Domain Warming 服務的擴充倍率表，並將查詢最高寄送量的方法從 findOne 改為 findPage。主要風險在於 #getHighestCount 的日期過濾條件從 `<` 改為 `<=`，可能導致今天的寄送量被納入計算，造成暖機限制不正確。此外，高量寄送者的上限邏輯在特定情況下可能造成限制下降，且測試中對 findPage 的模擬方式與實際 API 不一致。建議先修正日期過濾條件，並確認高量上限邏輯是否符合預期。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | 日期過濾條件從 `<` 改為 `<=` 可能納入今天的寄送量 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高量寄送者的上限邏輯可能導致限制下降 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 測試中對 findPage 的模擬方式與實際 API 不一致 | 0.75 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:63` | 測試中設定假時間的方式可能導致跨日問題 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> 日期過濾條件從 `<` 改為 `<=` 可能納入今天的寄送量</summary>

在 `#getHighestCount` 方法中，原本的過濾條件是 `created_at:<${today}`，但修改後變成 `created_at:<=${today}`。這會導致查詢結果包含今天建立的郵件，而註解明確指出要排除今天的寄送量（`excluding today`）。這可能造成暖機限制計算錯誤，例如若今天已寄出大量郵件，會使 `lastCount` 偏高，進而影響後續的擴充計算。建議改回 `<` 運算子，或使用 `created_at:<${new Date().toISOString().split('T')[0]}` 來確保只查詢今天之前的資料。

**判斷依據**：diff 中將 `created_at:<` 改為 `created_at:<=`，且方法註解仍寫著 `excluding today`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高量寄送者的上限邏輯可能導致限制下降</summary>

在 `getWarmupLimit` 中，當 `lastCount >= 400000` 時，計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 和 `absoluteIncrease = lastCount + 75000`，然後取兩者最小值。但若 `lastCount` 很大（例如 800000），`scaledIncrease` 為 960000，`absoluteIncrease` 為 875000，取最小值為 875000，這比 `lastCount` 本身還大，所以限制仍會增加。然而，若 `lastCount` 接近 400000，例如 400000，`scaledIncrease` 為 480000，`absoluteIncrease` 為 475000，取最小值為 475000，這比 `lastCount` 大，所以限制增加。但若 `lastCount` 為 500000，`scaledIncrease` 為 600000，`absoluteIncrease` 為 575000，取最小值為 575000，仍大於 `lastCount`。因此，此邏輯似乎不會造成限制下降，但需確認是否有可能因為浮點數或捨入問題導致限制小於 `lastCount`。建議加入測試案例驗證高量區間的行為，並考慮使用 `Math.max(lastCount, ...)` 確保限制不會下降。

**判斷依據**：diff 中新增的高量上限邏輯，但未處理限制可能小於 lastCount 的邊界情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 測試中對 findPage 的模擬方式與實際 API 不一致</summary>

在單元測試中，原本使用 `findOne` 的模擬被改為 `findPage`，但模擬的實作方式不一致。例如，在 `beforeEach` 中，`Email = createModelClass({ findAll: [] })`，但 `DomainWarmingService` 呼叫的是 `findPage`，這可能導致測試失敗或無法正確模擬。此外，在 `should query for emails created before today` 測試中，使用了 `sinon.stub().resolves({data: []})` 來模擬 `findPage`，但其他測試則使用 `createModelClass` 搭配 `findAll` 屬性，這可能造成混淆。建議統一使用 `sinon.stub()` 來模擬 `findPage`，並確保所有測試都正確設定回傳值。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中的模擬方式不一致，可能導致測試無法正確執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:63</code> 測試中設定假時間的方式可能導致跨日問題</summary>

在整合測試中，`setDay` 函式使用 `baseDate` 作為基準，並設定 `shouldAdvanceTime: true`。這可能導致測試中的時間自動前進，影響後續的日期計算。建議確認 `shouldAdvanceTime` 是否必要，或改用固定時間點以避免非預期的時間推進。

**判斷依據**：diff 中新增了 `shouldAdvanceTime: true`，可能導致測試中的時間非預期地前進。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8583 (cache hit 8576) ｜ completion tokens 1464 ｜ PR #3</sub>