<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了網域暖身的擴充倍率，從原本的 2 倍改為較保守的 1.25 倍起跳，並新增高流量（400k+）的成長上限。主要風險在於 `#getHighestCount` 改用 `findPage` 後，若底層 ORM 不支援 `findPage` 或回傳格式不符，可能導致暖身計算失效；另外 `getWarmupLimit` 的邊界條件（`<` vs `<=`）與高流量上限的計算方式需確認是否符合預期。測試已同步更新，但部分測試的斷言邏輯可能過於寬鬆。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:101` | 改用 findPage 可能導致查詢失敗或回傳格式不符 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高流量上限的計算可能不符合預期 | 0.75 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:132` | 邊界條件 `<` 與 `<=` 的差異可能造成非預期行為 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:68` | 測試中 Email 模型的 mock 方式可能與實際不符 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:101</code> 改用 findPage 可能導致查詢失敗或回傳格式不符</summary>

`#getHighestCount` 從 `findOne` 改為 `findPage`，但 `EmailModel` 型別定義中的 `findPage` 回傳 `{data: EmailRecord[]}`。若實際 ORM 的 `findPage` 方法不存在或回傳格式不同（例如直接回傳陣列），會造成執行時期錯誤。建議確認 `Email` 模型確實提供 `findPage` 方法，且回傳物件包含 `data` 陣列；若否，應改用其他查詢方式或調整型別。

**判斷依據**：diff 中 `#getHighestCount` 的實作從 `findOne` 改為 `findPage`，且型別定義也同步修改，但未提供 `findPage` 的實作或驗證其存在。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高流量上限的計算可能不符合預期</summary>

高流量（`lastCount >= 400000`）時，回傳 `Math.min(scaledIncrease, absoluteIncrease)`，其中 `scaledIncrease = Math.ceil(lastCount * 1.2)`，`absoluteIncrease = lastCount + 75000`。但 `scaledIncrease` 是「增加後總量」，而 `absoluteIncrease` 也是「增加後總量」，兩者取最小值可能導致成長幅度小於 20% 或 75k 的較小者。例如 `lastCount = 500000` 時，`scaledIncrease = 600000`，`absoluteIncrease = 575000`，回傳 575000，成長 15%，低於 20% 上限。若意圖是「成長不超過 20% 且不超過 75k」，應改為 `Math.min(lastCount * 1.2, lastCount + 75000)`，但需確認產品需求。

**判斷依據**：diff 中新增的高流量處理邏輯，`scaledIncrease` 與 `absoluteIncrease` 皆為總量，取最小值可能造成成長幅度低於任一限制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:132</code> 邊界條件 `<` 與 `<=` 的差異可能造成非預期行為</summary>

在 `getWarmupLimit` 中，原本使用 `lastCount <= threshold.limit`，現在改為 `lastCount < threshold.limit`。這會使得當 `lastCount` 恰好等於某個 threshold 的 `limit` 時，會落入下一個 threshold 的倍率。例如 `lastCount = 1000` 時，原本會套用 1.25 倍（因為 `<= 1000`），現在會套用 1.5 倍（因為 `< 1000` 不成立，進入下一個 threshold）。需確認此變更是否符合預期。

**判斷依據**：diff 中將 `<=` 改為 `<`，且測試案例中 `lastCount = 1000` 的預期值從 2000 改為 1250，但未說明此邊界變更的意圖。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:68</code> 測試中 Email 模型的 mock 方式可能與實際不符</summary>

在單元測試中，`Email` 模型被 mock 為 `createModelClass({ findAll: [...] })`，但 `DomainWarmingService` 實際呼叫的是 `findPage`。若 `createModelClass` 未正確將 `findAll` 轉換為 `findPage`，測試可能無法正確模擬行為。建議確認 `createModelClass` 的實作，或直接 mock `findPage` 方法。

**判斷依據**：diff 中多處測試將 `findOne` 改為 `findAll`，但服務程式碼使用 `findPage`，可能導致測試與實作不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8497 (cache hit 6272) ｜ completion tokens 1445 ｜ PR #3</sub>