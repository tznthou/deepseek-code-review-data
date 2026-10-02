<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Domain Warming 的擴充倍率，並將查詢從 findOne 改為 findPage。主要風險在於 #getHighestCount 的日期過濾條件從「<」改為「<=」，可能將今天的郵件納入計算，導致暖機上限膨脹；此外，單元測試中對 findPage 的模擬方式與實際使用不一致，可能造成測試誤判。整體邏輯尚可，但需修正日期過濾與測試模擬。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | 日期過濾條件從「<」改為「<=」可能納入今天的郵件 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 單元測試中 Email 模型的 findPage 模擬與實際使用不一致 | 0.75 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高流量分支的計算可能導致上限下降 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> 日期過濾條件從「<」改為「<=」可能納入今天的郵件</summary>

原本使用 `created_at:<今天日期` 排除今天的郵件，但改為 `created_at:<=今天日期` 後，會包含今天建立的郵件。這可能導致 #getHighestCount 回傳今天的郵件數量，進而讓暖機上限膨脹，甚至造成無限成長。建議維持原本的 `<` 運算子，或明確排除今天的郵件。

**判斷依據**：diff 中將 `filter: \`created_at:<${new Date().toISOString().split('T')[0]}\`` 改為 `filter: \`created_at:<=${new Date().toISOString().split('T')[0]}\``。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 單元測試中 Email 模型的 findPage 模擬與實際使用不一致</summary>

在 beforeEach 中，Email 被設定為 `createModelClass({ findAll: [] })`，但 DomainWarmingService 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未定義，進而拋出錯誤。建議改為 `createModelClass({ findPage: async () => ({ data: [] }) })` 或類似模擬。

**判斷依據**：diff 中將原本的 `findOne: null` 改為 `findAll: []`，但服務程式碼使用 `findPage`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高流量分支的計算可能導致上限下降</summary>

在 `lastCount >= 400000` 時，回傳 `Math.min(scaledIncrease, absoluteIncrease)`。其中 `scaledIncrease = Math.ceil(lastCount * 1.2)`，`absoluteIncrease = lastCount + 75000`。當 `lastCount` 大於 375000 時，`absoluteIncrease` 會小於 `scaledIncrease`，因此回傳 `lastCount + 75000`。這可能導致暖機上限的成長幅度低於預期，但仍在合理範圍內。建議確認此行為是否符合產品需求。

**判斷依據**：diff 中新增的高流量分支。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6264 (cache hit 1536) ｜ completion tokens 904 ｜ PR #3</sub>