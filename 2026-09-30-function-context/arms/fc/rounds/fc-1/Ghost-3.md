<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 domain warmup 的擴展因子，並將 Email 模型的查詢從 findOne 改為 findPage。整體邏輯合理，但存在兩個主要問題：高流量分支的計算可能導致目標上限低於當前值（例如 lastCount=400,000 時回傳 480,000，但 lastCount=500,000 時回傳 575,000，仍高於 400,000，但若 lastCount 接近 400,000 且 maxAbsoluteIncrease 較小時可能出現倒退），以及測試中對 findPage 的模擬方式與實際 API 不一致，可能導致測試誤判。建議修正高流量分支的計算邏輯，並確保測試模擬符合實際模型行為。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高流量分支可能導致目標上限低於當前值 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:123` | 測試中對 findPage 的模擬與實際 API 不一致 | 0.75 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | findPage 查詢的 filter 使用 <= 可能包含今日資料 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高流量分支可能導致目標上限低於當前值</summary>

在 `#getTargetLimit` 中，當 `lastCount >= 400_000` 時，計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 和 `absoluteIncrease = lastCount + 75_000`，然後取兩者最小值。但若 `lastCount` 接近 400,000，例如 400,000，則 `scaledIncrease = 480,000`，`absoluteIncrease = 475,000`，回傳 475,000，仍高於 400,000。但若 `lastCount` 為 500,000，則回傳 575,000，高於 500,000。然而，若 `lastCount` 為 400,000 且 `maxAbsoluteIncrease` 較小（例如 50,000），則可能回傳低於 `lastCount` 的值，導致目標上限倒退。目前設定下，`lastCount=400,000` 時回傳 475,000，仍高於 400,000，但若未來調整參數，可能出現倒退。建議明確確保回傳值至少為 `lastCount`，例如使用 `Math.max(lastCount, Math.min(scaledIncrease, absoluteIncrease))`。

**判斷依據**：diff 中新增的高流量分支計算，未保證結果大於等於 lastCount。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:123</code> 測試中對 findPage 的模擬與實際 API 不一致</summary>

在單元測試中，使用 `createModelClass({ findAll: [...] })` 來模擬 `findPage`，但 `createModelClass` 可能不會將 `findAll` 轉換為 `findPage` 方法。實際服務呼叫的是 `findPage`，若模擬物件沒有該方法，測試會拋出錯誤或無法正確模擬。建議直接建立包含 `findPage` 方法的模擬物件，例如 `Email = { findPage: async () => ({ data: [...] }) }`，或確認 `createModelClass` 的實作是否支援 `findAll` 轉換。

**判斷依據**：diff 中多處將原本的 `findOne` 模擬改為 `findAll`，但服務程式碼呼叫的是 `findPage`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> findPage 查詢的 filter 使用 <= 可能包含今日資料</summary>

原本 `findOne` 使用 `created_at:<${today}` 排除今日，但改為 `findPage` 後 filter 變成 `created_at:<=${today}`，這會包含今日建立的 email。若今日已有 email，則 `#getHighestCount` 可能取到今日的 csd_email_count，導致 warmup limit 計算錯誤。建議確認是否應排除今日，若需排除，應改回 `<`。

**判斷依據**：diff 中 filter 從 `<` 改為 `<=`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9171 (cache hit 1536) ｜ completion tokens 1139 ｜ PR #3</sub>