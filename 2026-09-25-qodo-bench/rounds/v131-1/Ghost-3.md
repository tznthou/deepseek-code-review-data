<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 調整了 Domain Warming 的擴充倍率，並將查詢從 findOne 改為 findPage。主要風險在於高量級（400k+）的計算邏輯：`Math.ceil(lastCount * 1.2)` 與 `lastCount + 75000` 取最小值，但若 lastCount 為 400,000，兩者皆為 480,000，與測試預期的 800,000 不符。此外，`getExpectedScale` 函式未涵蓋 100k–400k 的 2× 倍率，可能導致測試斷言錯誤。建議修正高量級計算邏輯並補齊測試。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:126` | 高量級（400k+）計算邏輯錯誤 | 0.95 |
| ⚠️ | Major | `ghost/core/test/integration/services/email-service/domain-warming.test.js:290` | getExpectedScale 函式未涵蓋 100k–400k 的 2× 倍率 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:126</code> 高量級（400k+）計算邏輯錯誤</summary>

在 `getWarmupLimit` 中，當 `lastCount >= 400000` 時，程式碼計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 與 `absoluteIncrease = lastCount + 75000`，並回傳兩者最小值。但若 `lastCount` 為 400,000，`scaledIncrease` 為 480,000，`absoluteIncrease` 為 475,000，回傳 475,000，與測試預期的 800,000 不符。此邏輯與註解「cap the increase at 20% or 75k absolute」矛盾，應為 `Math.min(lastCount * 1.2, lastCount + 75000)`，但需確認預期行為。

**判斷依據**：diff 中新增的程式碼片段，以及測試檔案中 `{lastCount: 400000, expected: 800000}` 的測試案例。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:290</code> getExpectedScale 函式未涵蓋 100k–400k 的 2× 倍率</summary>

在整合測試中，`getExpectedScale` 函式僅處理 `count <= 100`、`<= 1000`、`<= 5000` 的情況，其餘回傳 `Math.ceil(count * 1.75)`。但根據新的 scaling table，當 `count` 介於 100k 到 400k 時，倍率應為 2×。這將導致測試在該區間斷言失敗。

**判斷依據**：diff 中新增的 `getExpectedScale` 函式，以及 scaling table 中 `{ limit: 100_000, scale: 1.75 }` 與 `{ limit: 400_000, scale: 2 }` 的定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6228 (cache hit 1408) ｜ completion tokens 890 ｜ PR #3</sub>