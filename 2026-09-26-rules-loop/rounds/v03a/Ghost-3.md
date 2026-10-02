<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Domain Warming 的擴充倍率，並將查詢最高寄送量的方法從 findOne 改為 findPage。主要風險在於邊界條件處理（如 lastCount 等於 400,000 時的行為）以及測試中對時間模擬的變更可能影響測試穩定性。建議先確認高量寄送者的計算邏輯與測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:125` | 高量寄送者（lastCount >= 400,000）的計算可能與預期不符 | 0.80 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:63` | 測試中時間模擬的變更可能導致不穩定 | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:102` | findPage 的 filter 條件可能包含當天資料 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:125</code> 高量寄送者（lastCount >= 400,000）的計算可能與預期不符</summary>

在 `getWarmupLimit` 中，當 `lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold`（400,000）時，程式會計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 和 `absoluteIncrease = lastCount + 75,000`，然後回傳兩者較小值。但若 `lastCount` 恰好等於 400,000，則 `scaledIncrease = 480,000`，`absoluteIncrease = 475,000`，回傳 475,000。然而，根據測試案例（`{lastCount: 400000, expected: 800000}`），預期值為 800,000，顯示此處邏輯可能與測試不一致。建議確認高量寄送者的預期行為，並修正程式或測試。

**判斷依據**：diff 中新增的 highVolume 處理區塊，以及測試檔案中 `{lastCount: 400000, expected: 800000}` 的案例。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:63</code> 測試中時間模擬的變更可能導致不穩定</summary>

`setDay` 函式改為使用 `sinon.useFakeTimers({ now: time.getTime(), shouldAdvanceTime: true })`。`shouldAdvanceTime: true` 會讓 fake timers 自動推進時間，可能影響依賴時間的測試（例如 `created_at` 的比較）。建議確認此變更是否必要，並考慮使用 `shouldAdvanceTime: false` 或明確控制時間推進。

**判斷依據**：diff 中 `setDay` 函式的修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:102</code> findPage 的 filter 條件可能包含當天資料</summary>

`#getHighestCount` 使用 `filter: \`created_at:<=${new Date().toISOString().split('T')[0]}\``，這會包含當天建立的郵件。原本的 `findOne` 使用 `created_at:<`（不包含當天），但新程式碼改為 `<=`，可能導致取得當天的最高寄送量，影響 warmup 計算。建議確認是否應排除當天資料。

**判斷依據**：diff 中 filter 條件的變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8583 (cache hit 6144) ｜ completion tokens 971 ｜ PR #3</sub>