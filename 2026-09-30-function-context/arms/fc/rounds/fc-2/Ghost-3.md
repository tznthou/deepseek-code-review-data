<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 調整了 Domain Warming 的擴展因子，並將資料查詢從 findOne 改為 findPage。主要風險在於 #getTargetLimit 的邊界條件處理：lastCount 等於 1000 或 5000 時，會落入較低的 multiplier 區間，可能導致暖機進度倒退。此外，測試中對 findPage 的模擬方式與實際回傳結構不一致，可能造成測試誤判。建議修正邊界條件並統一測試模擬。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:132` | 邊界條件錯誤：lastCount 等於 1000 或 5000 時會套用較低的 multiplier | 0.95 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:15` | 測試中對 findPage 的模擬與實際回傳結構不一致 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | findPage 的 filter 使用 `<=` 可能包含今天的郵件 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:131` | thresholds 陣列在每次呼叫時重新排序，可能造成不必要的效能開銷 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:132</code> 邊界條件錯誤：lastCount 等於 1000 或 5000 時會套用較低的 multiplier</summary>

在 `#getTargetLimit` 中，threshold 的判斷從 `<=` 改為 `<`，導致 `lastCount` 正好等於 1000 或 5000 時，會落入下一個較低的 multiplier 區間。例如 `lastCount = 1000` 時，原本應套用 1.5×（因為 1000 ≤ 5000），但現在會套用 1.25×（因為 1000 < 5000 且 1000 > 1000 不成立，所以落入 1.25× 區間）。這會造成暖機進度倒退，與預期的單調遞增行為不符。

建議將判斷改回 `<=`，或調整 thresholds 的定義以明確包含邊界值。

**判斷依據**：diff 中將原本的 `if (lastCount <= threshold.limit)` 改為 `if (lastCount < threshold.limit)`，且 thresholds 定義為 `{limit: 1_000, scale: 1.25}` 和 `{limit: 5_000, scale: 1.5}`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:15</code> 測試中對 findPage 的模擬與實際回傳結構不一致</summary>

在 `beforeEach` 中，`Email` 被初始化為 `createModelClass({ findAll: [] })`，但服務實際呼叫的是 `findPage`。這可能導致測試中 `findPage` 未被正確 stub，而回傳 undefined，進而使 `result.data.length` 拋出錯誤。雖然部分測試有覆寫 `Email`，但未覆寫的測試（如 `constructor`、`isEnabled`）可能受到影響。

建議統一使用 `findPage` 進行模擬，或確保 `createModelClass` 能正確處理 `findPage`。

**判斷依據**：diff 中將原本的 `findOne: null` 改為 `findAll: []`，但服務程式碼已改用 `findPage`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> findPage 的 filter 使用 `<=` 可能包含今天的郵件</summary>

原本的 filter 是 `created_at:<${date}`，現在改為 `created_at:<=${date}`。這會將建立時間為今天的郵件也納入計算，可能導致 `lastCount` 包含今天的發送量，進而影響暖機限制的計算。如果目的是排除今天的郵件，應維持 `<`。

請確認此變更是否為預期行為。

**判斷依據**：diff 中將 filter 從 `created_at:<` 改為 `created_at:<=`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:131</code> thresholds 陣列在每次呼叫時重新排序，可能造成不必要的效能開銷</summary>

在 `#getTargetLimit` 中，每次呼叫都會對 `WARMUP_SCALING_TABLE.thresholds` 進行 `sort`。雖然陣列很小，但這是重複的計算。建議在定義時就排序好，或使用已排序的常數。

**判斷依據**：diff 中保留了原本的 `sort` 呼叫，但 thresholds 已在定義時按順序排列。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9171 (cache hit 9088) ｜ completion tokens 1219 ｜ PR #3</sub>