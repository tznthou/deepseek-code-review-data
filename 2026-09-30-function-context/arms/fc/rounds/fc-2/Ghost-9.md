<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Domain Warming 的計算方式從「依前次發送量乘上倍率」改為「依時間指數成長」。整體方向合理，但存在幾個關鍵問題：`getWarmupLimit` 在暖機完成後回傳 `Infinity`，可能導致下游將所有郵件都分配到自訂網域，造成發送延遲或信譽風險；`#getDaysSinceFirstEmail` 的日期計算使用 `Math.ceil`，可能因時區或時間差導致天數計算不準確；此外，測試中使用了 `Math.round` 而非實作中的 `Math.floor`，可能造成測試與實作不一致。建議先修正 `Infinity` 的處理方式，並確認日期計算的邊界條件。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | 暖機完成後回傳 Infinity 可能導致所有郵件都從自訂網域發送 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 日期計算使用 Math.ceil 可能導致天數計算不準確 | 0.80 |
| ⚠️ | Major | `ghost/core/test/integration/services/email-service/domain-warming.test.js:302` | 測試中使用 Math.round 與實作中的 Math.floor 不一致 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:66` | 查詢條件 `csd_email_count:-null` 可能無法正確過濾 null 值 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> 暖機完成後回傳 Infinity 可能導致所有郵件都從自訂網域發送</summary>

當 `day > totalDays` 時，`getWarmupLimit` 回傳 `Infinity`。這會使呼叫端（例如批次發送服務）將所有郵件都分配到自訂網域，完全繞過 fallback 網域。若自訂網域尚未完全建立信譽，可能導致大量郵件被歸類為垃圾郵件或發送延遲。建議回傳 `emailCount`（即不限制）或設定一個明確的最大值，而不是 `Infinity`。

**判斷依據**：diff 中新增的程式碼片段：`if (day > this.#warmupConfig.totalDays) { return Infinity }`。此行為與先前版本不同，先前版本會回傳一個有限值（`Math.min(emailCount, targetLimit)`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 日期計算使用 Math.ceil 可能導致天數計算不準確</summary>

`#getDaysSinceFirstEmail` 使用 `Math.ceil((Date.now() - firstEmailTime) / (1000 * 60 * 60 * 24))` 來計算天數。這會將任何不滿 24 小時的差都進位為 1 天，導致在第一天內發送多封郵件時，第二封郵件可能被視為第 1 天而非第 0 天，造成暖機進度提前。建議改用 `Math.floor` 或明確的日曆天計算。

**判斷依據**：diff 中新增的程式碼片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:302</code> 測試中使用 Math.round 與實作中的 Math.floor 不一致</summary>

在整合測試的 `getExpectedLimit` 函式中，使用了 `Math.round` 來計算期望值，但實作中 `getWarmupLimit` 使用的是 `Math.floor`。這可能導致在某些天數下測試期望值與實作結果不同，造成測試不穩定或錯誤。建議統一使用 `Math.floor` 或調整實作以符合測試。

**判斷依據**：diff 中測試程式碼片段：`return Math.round(start * Math.pow(end / start, day / (totalDays - 1)));`，而實作中為 `Math.floor(...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:66</code> 查詢條件 `csd_email_count:-null` 可能無法正確過濾 null 值</summary>

在 `#getDaysSinceFirstEmail` 中，使用 `filter: 'csd_email_count:-null'` 來查詢有 `csd_email_count` 的郵件。但根據 Ghost 的查詢語法，`-null` 可能不是有效的運算子，或者無法正確過濾 null 值。建議確認正確的過濾方式，例如使用 `csd_email_count:>0` 或 `csd_email_count:not null`。

**判斷依據**：diff 中新增的程式碼片段：`filter: 'csd_email_count:-null',`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10688 (cache hit 10624) ｜ completion tokens 1267 ｜ PR #9</sub>