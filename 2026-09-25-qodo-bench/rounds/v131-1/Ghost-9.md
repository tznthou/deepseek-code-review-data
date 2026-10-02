<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Domain Warming 的郵件量限制從「依前次發送量乘上倍率」改為「依時間指數成長」。整體方向合理，但存在幾個關鍵問題：`getWarmupLimit` 在暖機完成後回傳 `Infinity`，可能導致呼叫端未預期的行為；`#getDaysSinceFirstEmail` 的日期計算可能因時區或時序產生 off-by-one；測試中對指數公式的預期值使用 `Math.round` 而實作使用 `Math.floor`，可能造成不一致。建議先修正這些問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | 暖機完成後回傳 Infinity 可能導致呼叫端錯誤 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 日期計算可能因時區或時序產生 off-by-one | 0.80 |
| ⚠️ | Major | `ghost/core/test/integration/services/email-service/domain-warming.test.js:302` | 測試預期值使用 Math.round 與實作 Math.floor 不一致 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:66` | 查詢條件 `csd_email_count:-null` 可能無法正確過濾 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> 暖機完成後回傳 Infinity 可能導致呼叫端錯誤</summary>

`getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有除法或轉換可能出錯）。建議回傳 `emailCount` 或一個明確的常數（如 `Number.MAX_SAFE_INTEGER`），並在文件說明。

**判斷依據**：diff 中新增的 `return Infinity` 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 日期計算可能因時區或時序產生 off-by-one</summary>

`#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並取 `Math.ceil`。若 `created_at` 是 UTC 儲存，而伺服器時區非 UTC，可能導致天數計算偏差。此外，若第一封信是在當天稍晚發送，`Math.ceil` 可能將未滿一天算成一天。建議使用 UTC 日期或明確的日界線計算。

**判斷依據**：diff 中新增的日期計算行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/test/integration/services/email-service/domain-warming.test.js:302</code> 測試預期值使用 Math.round 與實作 Math.floor 不一致</summary>

測試中的 `getExpectedLimit` 使用 `Math.round`，而實作使用 `Math.floor`。這可能導致測試在某些天數下預期值與實際值相差 1，造成測試不穩定或誤報。建議統一使用 `Math.floor` 或調整實作。

**判斷依據**：diff 中測試新增的 `getExpectedLimit` 函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:66</code> 查詢條件 `csd_email_count:-null` 可能無法正確過濾</summary>

`filter: 'csd_email_count:-null'` 的語法可能不正確，Ghost 的 filter 通常使用 `csd_email_count:not null` 或 `csd_email_count:!=null`。若語法錯誤，可能導致查詢失敗或回傳所有記錄。建議確認正確的 filter 語法。

**判斷依據**：diff 中修改的 filter 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7555 (cache hit 1408) ｜ completion tokens 1030 ｜ PR #9</sub>