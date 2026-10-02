<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 調整了 Domain Warming 的擴充倍率，並將查詢從 findOne 改為 findPage。主要風險在於高量級（400k+）的計算邏輯：當 lastCount 為 400,000 時，回傳值為 800,000（2 倍），但下一個測試案例 500,000 卻回傳 575,000，顯示在 400k 邊界處的倍率不連續，可能導致寄送量突然暴增。此外，測試中對 findPage 的模擬方式不一致，可能造成測試與實作脫節。建議先修正高量級計算邏輯，並統一測試模擬方式。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:125` | 高量級（400k+）的計算邏輯在邊界處不連續，可能導致寄送量暴增 | 0.95 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:68` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:83` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:99` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:112` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:128` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:149` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:164` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:213` | 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:125</code> 高量級（400k+）的計算邏輯在邊界處不連續，可能導致寄送量暴增</summary>

在 `getWarmupLimit` 中，當 `lastCount` 等於 `highVolume.threshold`（400,000）時，會先進入 `if (lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold)` 分支，回傳 `Math.min(400000 * 1.2, 400000 + 75000) = Math.min(480000, 475000) = 475000`。但根據測試案例，`lastCount = 400000` 的預期值是 800000（2 倍），這表示在 400k 邊界處，倍率從 2 倍突然降為 1.2 倍，造成不連續。這可能導致在達到 400k 後，寄送量突然大幅下降，影響 warmup 效果。建議調整 `highVolume.threshold` 或計算邏輯，使倍率在邊界處連續。

**判斷依據**：diff 中新增的 highVolume 分支，以及測試案例 `{lastCount: 400000, expected: 800000}` 與 `{lastCount: 500000, expected: 575000}` 的矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `beforeEach` 中，`Email` 被設定為 `createModelClass({ findAll: [] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:68</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `should return 200 when no previous emails exist` 測試中，`Email` 被設定為 `createModelClass({ findAll: [] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:83</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `should return 200 when highest count is 0` 測試中，`Email` 被設定為 `createModelClass({ findAll: [{ csd_email_count: 0 }] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:99</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `should return emailCount when it is less than calculated limit` 測試中，`Email` 被設定為 `createModelClass({ findAll: [{ csd_email_count: 1000 }] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:112</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `should return calculated limit when emailCount is greater` 測試中，`Email` 被設定為 `createModelClass({ findAll: [{ csd_email_count: 1000 }] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:128</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `should handle csd_email_count being null` 測試中，`Email` 被設定為 `createModelClass({ findAll: [{ csd_email_count: null }] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:149</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `should handle csd_email_count being undefined` 測試中，`Email` 被設定為 `createModelClass({ findAll: [{}] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:164</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `should query for emails created before today` 測試中，`Email` 被設定為 `{ findPage: findPageStub }`，但其他測試使用 `createModelClass` 搭配 `findAll`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:213</code> 測試中對 findPage 的模擬方式不一致，可能導致測試與實作脫節</summary>

在 `should return correct warmup progression through the stages` 測試中，`EmailModel` 被設定為 `createModelClass({ findAll: [{ csd_email_count: testCase.lastCount }] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確模擬，而實際執行時會呼叫到未定義的方法。建議統一使用 `findPage` 進行模擬，或確認 `createModelClass` 能正確處理 `findAll` 與 `findPage` 的對應關係。

**判斷依據**：diff 中將 `findOne` 改為 `findPage`，但測試中仍使用 `findAll` 進行模擬。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8563 (cache hit 8448) ｜ completion tokens 3144 ｜ PR #3</sub>