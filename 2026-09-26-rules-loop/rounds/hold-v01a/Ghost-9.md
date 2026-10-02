<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 DomainWarmingService 從基於前次發送量的暖機策略改為基於時間的指數成長策略。主要風險在於 `#getDaysSinceFirstEmail` 的日期計算可能因時區或 DST 造成 off-by-one，且 `getWarmupLimit` 回傳 `Infinity` 可能導致呼叫端未預期的行為。測試覆蓋完整，但部分測試使用 `Math.round` 與實作 `Math.floor` 不一致，可能造成測試脆弱。建議先確認日期計算的時區處理與 `Infinity` 的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 日期計算可能因時區或 DST 造成 off-by-one | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | 回傳 Infinity 可能導致呼叫端未預期行為 | 0.70 |
| 🔸 | Minor | `ghost/core/test/integration/services/email-service/domain-warming.test.js:302` | 測試使用 Math.round 與實作 Math.floor 不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 日期計算可能因時區或 DST 造成 off-by-one</summary>

`#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的 timestamp 差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或跨越 DST 轉換，可能導致天數計算多一天或少一天，進而影響暖機限制。建議改用 UTC 日曆日差（例如將兩個日期轉為 UTC 日期字串後相減），或明確指定時區。

**判斷依據**：diff 中新增的這一行直接使用毫秒差除以固定毫秒數，未考慮時區或 DST。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> 回傳 Infinity 可能導致呼叫端未預期行為</summary>

當暖機天數超過 `totalDays` 時，`getWarmupLimit` 回傳 `Infinity`。若呼叫端將此值用於後續計算（例如分配郵件數量），可能產生非預期結果。建議回傳一個明確的數值（例如 `emailCount`）或定義一個特殊常數，並在文件說明。

**判斷依據**：diff 中新增的這段程式碼直接回傳 `Infinity`，未見呼叫端處理此值的邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:302</code> 測試使用 Math.round 與實作 Math.floor 不一致</summary>

測試中的 `getExpectedLimit` 使用 `Math.round`，但實作使用 `Math.floor`。這可能導致在某些天數下測試期望值與實作結果不同，造成測試脆弱。建議測試與實作使用相同的捨入方式。

**判斷依據**：diff 中測試新增的這一行使用 `Math.round`，而實作在 `DomainWarmingService.ts` 中使用 `Math.floor`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9900 (cache hit 7552) ｜ completion tokens 849 ｜ PR #9</sub>