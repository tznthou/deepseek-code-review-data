<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Domain Warming 的擴充倍率，從原本的 2 倍、1.5 倍改為更保守的 1.25、1.5、1.75、2 倍，並為高量寄件者（400k+）加上 1.2 倍或 +75k 的上限。同時將查詢最高寄件量的方法從 findOne 改為 findPage，並更新相關測試。主要風險在於 findPage 的實作與測試替身不一致，可能導致測試誤判；此外，高量上限的計算方式與註解描述有出入，需確認是否符合預期。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20` | 測試替身使用 findAll 而非 findPage，可能導致測試無法正確模擬 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高量上限的計算可能與註解描述不符 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | findPage 的 filter 條件從 `<` 改為 `<=`，可能包含今日的郵件 | 0.70 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:63` | 測試中 fake timers 的 shouldAdvanceTime 可能導致非預期行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/unit/server/services/email-service/domain-warming-service.test.ts:20</code> 測試替身使用 findAll 而非 findPage，可能導致測試無法正確模擬</summary>

在 beforeEach 中，Email 模型被建立為 `createModelClass({ findAll: [] })`，但 DomainWarmingService 呼叫的是 `findPage`。這可能導致測試中 `findPage` 未定義，進而拋出錯誤或回傳非預期結果。請確認 `createModelClass` 的實作是否會將 `findAll` 映射到 `findPage`，否則應改為 `findPage: sinon.stub().resolves({ data: [] })` 或類似方式。

**判斷依據**：diff 中將原本的 `findOne: null` 改為 `findAll: []`，但服務程式碼使用的是 `findPage`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高量上限的計算可能與註解描述不符</summary>

註解說明高量時「cap the increase at 20% or 75k absolute」，但程式碼計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 與 `absoluteIncrease = lastCount + 75_000`，然後取 `Math.min`。這代表當 `lastCount` 大於 375,000 時，`absoluteIncrease` 會小於 `scaledIncrease`，因此上限會是 +75k，而非 20%。例如 `lastCount = 500,000` 時，結果為 575,000（+75k），而非 600,000（+20%）。請確認此行為是否符合預期，或調整註解與實作。

**判斷依據**：diff 中新增的高量處理邏輯，與上方註解描述不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> findPage 的 filter 條件從 `<` 改為 `<=`，可能包含今日的郵件</summary>

原本使用 `created_at:<${today}` 排除今日，現在改為 `created_at:<=${today}`，這會包含今天建立的郵件。若今日已有寄件，可能會影響最高寄件量的計算，導致暖機限制過高。請確認此變更是否為預期行為。

**判斷依據**：diff 中將 `<` 改為 `<=`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:63</code> 測試中 fake timers 的 shouldAdvanceTime 可能導致非預期行為</summary>

在 `setDay` 中，`sinon.useFakeTimers` 使用了 `shouldAdvanceTime: true`，這會讓計時器自動前進。若測試中有依賴真實時間的邏輯，可能會受到影響。請確認此設定是否必要，或考慮使用 `shouldAdvanceTime: false`。

**判斷依據**：diff 中新增了 `shouldAdvanceTime: true`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8573 (cache hit 6144) ｜ completion tokens 1174 ｜ PR #3</sub>