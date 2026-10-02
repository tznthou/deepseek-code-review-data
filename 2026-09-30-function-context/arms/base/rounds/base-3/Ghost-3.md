<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Domain Warming 的擴充倍率，將原本較激進的倍增改為較保守的階段式成長，並加入高量寄送（400k+）的成長上限。主要風險在於 `#getHighestCount` 從 `findOne` 改為 `findPage` 後，若 `findPage` 回傳的資料結構與預期不符（例如缺少 `data` 陣列或 `get` 方法），可能導致執行時期錯誤。此外，測試中對 `findPage` 的模擬方式與實際模型行為可能不一致，需確認整合測試能涵蓋此變更。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:101` | `findPage` 回傳值可能未定義 `data` 屬性，導致執行時期錯誤 | 0.80 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 測試中 `createModelClass` 的 `findAll` 屬性與實際 `findPage` 不一致 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:111` | `get` 方法可能不存在於回傳的資料物件 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:101</code> `findPage` 回傳值可能未定義 `data` 屬性，導致執行時期錯誤</summary>

`#getHighestCount` 改為呼叫 `findPage` 後，直接存取 `result.data.length`。若 `findPage` 的實作在某些情況下（例如資料庫錯誤、回傳格式不符）未提供 `data` 陣列，將拋出 `TypeError`。建議先檢查 `result` 與 `result.data` 是否存在，或使用選用鏈結（`result?.data?.length`）並提供預設值。

**判斷依據**：diff 中 `#getHighestCount` 方法從 `findOne` 改為 `findPage`，並直接使用 `result.data.length`，但未對 `result` 或 `result.data` 進行空值檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 測試中 `createModelClass` 的 `findAll` 屬性與實際 `findPage` 不一致</summary>

在 `beforeEach` 中，`Email = createModelClass({ findAll: [] })`，但服務實際呼叫的是 `findPage`。這可能導致測試未正確模擬 `findPage` 的行為，使測試無法有效驗證服務邏輯。建議將 `findAll` 改為 `findPage` 或確認 `createModelClass` 如何處理 `findPage`。

**判斷依據**：diff 中 `beforeEach` 的 `Email` 初始化使用 `findAll`，但服務程式碼呼叫 `findPage`，兩者名稱不符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:111</code> `get` 方法可能不存在於回傳的資料物件</summary>

`result.data[0].get('csd_email_count')` 假設 `data` 陣列中的元素具有 `get` 方法。若 `findPage` 回傳的是純物件而非模型實例，將導致錯誤。建議確認 `findPage` 的回傳型別，或改用屬性存取（如 `result.data[0].csd_email_count`）。

**判斷依據**：diff 中直接呼叫 `get` 方法，但型別定義 `EmailModel` 的 `findPage` 回傳 `{data: EmailRecord[]}`，而 `EmailRecord` 型別未定義 `get` 方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6264 (cache hit 6144) ｜ completion tokens 974 ｜ PR #3</sub>