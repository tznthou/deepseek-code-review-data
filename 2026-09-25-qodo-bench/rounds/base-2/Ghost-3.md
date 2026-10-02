<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Domain Warming 的擴充倍率，從原本的 2x/1.5x 改為更保守的 1.25x/1.5x/1.75x/2x，並針對高流量（400k+）設定上限。同時將資料查詢從 findOne 改為 findPage，並更新相關測試。主要風險在於 findPage 的實作與測試替身不一致、日期過濾條件變更可能造成語意差異，以及高流量上限的計算方式可能與預期不符。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:101` | findPage 的呼叫方式可能與實際模型 API 不符 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 測試替身使用 findAll 而非 findPage，與實際程式碼不符 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | 日期過濾條件從 `<` 改為 `<=` 可能包含今日資料 | 0.70 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高流量上限的計算可能與註解不符 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:164` | 測試中對 findPage 的 stub 回傳結構可能不完整 | 0.60 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:207` | 測試案例中對高流量上限的預期值可能錯誤 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:101</code> findPage 的呼叫方式可能與實際模型 API 不符</summary>

程式碼將 `findOne` 改為 `findPage`，但 `findPage` 通常需要 `page` 參數，且回傳結構可能包含 `meta`。此處僅傳入 `filter`、`order`、`limit`，可能導致執行時錯誤或無法取得正確資料。建議確認 `findPage` 的實際簽名，或改用 `findAll` 搭配 `limit`。

**判斷依據**：diff 中新增的 `findPage` 呼叫，但未提供 `page` 參數，且回傳型別僅定義 `{data: EmailRecord[]}`，可能與實際模型不符。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 測試替身使用 findAll 而非 findPage，與實際程式碼不符</summary>

在單元測試中，`Email` 模型被設定為 `createModelClass({ findAll: [...] })`，但實際服務使用的是 `findPage`。這會導致測試無法正確模擬服務的行為，可能造成測試通過但實際執行失敗。建議將測試替身改為 `findPage` 並回傳 `{data: [...]}` 結構。

**判斷依據**：diff 中測試檔案將 `findOne` 改為 `findAll`，但服務程式碼使用的是 `findPage`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> 日期過濾條件從 `<` 改為 `<=` 可能包含今日資料</summary>

原本使用 `created_at:<今天` 排除今日建立的郵件，改為 `<=` 後會包含今日建立的郵件。這可能導致 `#getHighestCount` 取得今日的資料，進而影響暖機限制的計算。若今日已有大量寄送，可能造成限制過高。建議確認此變更是否為預期行為。

**判斷依據**：diff 中將 `<` 改為 `<=`，且註解仍寫「excluding today」，但實際條件已包含今日。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高流量上限的計算可能與註解不符</summary>

註解寫「cap the increase at 20% or 75k absolute」，但程式碼使用 `Math.ceil(lastCount * maxScale)` 計算 scaledIncrease，其中 `maxScale` 為 1.2，代表增加 20%，但 `Math.ceil` 可能導致增加超過 20%。此外，`absoluteIncrease` 是 `lastCount + maxAbsoluteIncrease`，但 `Math.min` 比較的是 scaledIncrease 與 absoluteIncrease，而非增加量。若 lastCount 很大，scaledIncrease 可能遠大於 absoluteIncrease，導致實際增加量超過 75k。建議重新檢視此邏輯。

**判斷依據**：diff 中新增的高流量處理邏輯，與註解描述不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:164</code> 測試中對 findPage 的 stub 回傳結構可能不完整</summary>

在「should query for emails created before today」測試中，`findPageStub` 回傳 `{data: []}`，但未包含 `meta` 等可能被服務使用的屬性。若服務未來使用 `meta`，測試可能無法涵蓋。建議確認 `findPage` 的完整回傳結構並在 stub 中提供。

**判斷依據**：diff 中新增的 stub 回傳物件僅有 `data` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:207</code> 測試案例中對高流量上限的預期值可能錯誤</summary>

在測試案例中，`{lastCount: 400000, expected: 800000}` 預期 400k 時回傳 800k，但根據程式碼，400k 已達 `highVolume.threshold`，應進入高流量處理，回傳 `min(400000*1.2, 400000+75000) = min(480000, 475000) = 475000`。此測試案例可能無法通過。建議修正預期值或調整程式碼邏輯。

**判斷依據**：diff 中測試案例的預期值與程式碼邏輯不符。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6264 (cache hit 6144) ｜ completion tokens 1647 ｜ PR #3</sub>