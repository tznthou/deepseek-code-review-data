<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Domain Warming 的擴充倍率，從原本的 2 倍/1.5 倍改為更保守的 1.25/1.5/1.75/2 倍，並針對高量寄送（400k+）設定上限。主要風險在於 `#getHighestCount` 改用 `findPage` 後，若 `findPage` 回傳的資料結構不符預期（例如 `data` 不是陣列或元素沒有 `get` 方法），可能導致執行時期錯誤。另外，`getWarmupLimit` 中對 `lastCount` 的邊界處理（`<` 與 `<=`）需確認是否與預期一致。測試涵蓋了新的倍率，但未驗證 `findPage` 的呼叫參數是否正確（例如 `limit: 1`）。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:101` | findPage 回傳結構假設可能導致執行時期錯誤 | 0.80 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:180` | 測試未驗證 findPage 的呼叫參數 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:125` | 高量寄送上限計算可能產生非預期結果 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:101</code> findPage 回傳結構假設可能導致執行時期錯誤</summary>

`#getHighestCount` 假設 `findPage` 回傳的 `data` 是陣列且每個元素都有 `get` 方法。若 `findPage` 的實作或 mock 回傳 `{data: null}` 或 `{data: [{}]}`，則 `result.data.length` 或 `result.data[0].get(...)` 會拋出錯誤。建議加入防禦性檢查，例如 `if (!result?.data?.length) return 0;` 並確認 `result.data[0]` 存在且 `get` 為函式。

**判斷依據**：diff 中新增的 `findPage` 呼叫與後續對 `result.data` 的直接存取，未檢查 `result.data` 是否為陣列或元素是否具有 `get` 方法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:180</code> 測試未驗證 findPage 的呼叫參數</summary>

在 `should query for emails created before today` 測試中，僅驗證了 `filter`、`order` 和 `limit` 的存在，但未驗證 `filter` 是否正確使用 `<=` 而非 `<`，也未驗證 `limit` 是否為 1。建議加入更精確的斷言，例如 `assert.equal(callArgs.limit, 1)` 和 `assert.ok(callArgs.filter.includes('created_at:<=<today>'))`。

**判斷依據**：diff 中測試僅檢查 `filter` 包含 `created_at:<`，但實際程式碼使用 `<=`，可能導致測試通過但實作錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:125</code> 高量寄送上限計算可能產生非預期結果</summary>

在 `lastCount >= 400_000` 時，`scaledIncrease = Math.ceil(lastCount * 1.2)` 與 `absoluteIncrease = lastCount + 75_000` 取最小值。若 `lastCount` 極大（例如 10,000,000），`scaledIncrease` 為 12,000,000，`absoluteIncrease` 為 10,075,000，取最小值為 10,075,000，仍可能造成單日寄送量大幅增加。建議確認此上限是否符合業務需求，或考慮更嚴格的絕對上限。

**判斷依據**：diff 中新增的高量處理邏輯，未對 `lastCount` 設定絕對上限，僅以比例與絕對增量取最小值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8573 (cache hit 8448) ｜ completion tokens 1211 ｜ PR #3</sub>