<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 domain warming 的擴充倍率，並將查詢最高寄送量的方法從 findOne 改為 findPage。主要風險在於 findPage 的 filter 條件從 `<` 改為 `<=`，可能導致當天已寄送的郵件被納入計算，造成暖機限制過高；此外，測試中對 findPage 的 mock 設定可能與實際實作不符，導致測試無法有效驗證。整體而言，邏輯變更合理，但需修正日期過濾條件並確認測試 mock 的正確性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | 日期過濾條件從 `<` 改為 `<=` 可能包含當天已寄送的郵件 | 0.80 |
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 測試中 mock 的 `findPage` 可能與實際模型不符 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:181` | 測試斷言仍檢查舊的 `<` 條件，與新程式碼不符 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> 日期過濾條件從 `<` 改為 `<=` 可能包含當天已寄送的郵件</summary>

在 `#getHighestCount` 中，filter 條件從 `created_at:<${today}` 改為 `created_at:<=${today}`。這會將當天建立的郵件也納入查詢，可能導致 `lastCount` 包含今天的寄送量，使得暖機限制計算過高。例如，若今天已寄出 1000 封，`lastCount` 可能變成 1000，導致明天的限制從 200 變成 1250，跳過暖機階段。建議改回 `<` 以排除當天資料。

**判斷依據**：diff 中將 `created_at:<` 改為 `created_at:<=`，且註解仍寫「excluding today」，但實際條件已包含今天。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 測試中 mock 的 `findPage` 可能與實際模型不符</summary>

在 `beforeEach` 中，`Email` 被設定為 `createModelClass({ findAll: [] })`，但 `DomainWarmingService` 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未定義而拋出錯誤，或回傳非預期結果。建議確認 `createModelClass` 的實作是否會將 `findAll` 轉換為 `findPage`，或直接 mock `findPage`。

**判斷依據**：diff 中將 `findOne: null` 改為 `findAll: []`，但服務程式碼呼叫 `findPage`，兩者名稱不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:181</code> 測試斷言仍檢查舊的 `<` 條件，與新程式碼不符</summary>

在測試 `should query for emails created before today` 中，斷言 `callArgs.filter.includes(`created_at:<${today}`)`，但實際程式碼已改為 `<=`。這會導致測試失敗。建議更新斷言以匹配新的過濾條件。

**判斷依據**：diff 中此斷言未變更，但服務程式碼的 filter 已改為 `<=`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8573 (cache hit 8448) ｜ completion tokens 882 ｜ PR #3</sub>