<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Tinybird v2 端點與 materialized view，並將版本控制從 query parameter 改為 config 中的 version 屬性。主要風險在於 `getStatEndpointUrl` 的版本前綴邏輯與 `tinybird.js` 的後綴邏輯不一致，可能導致前端與後端呼叫不同端點；另外 `filtered_sessions_v2.pipe` 的 session 屬性過濾條件未涵蓋所有 UTM 參數，可能造成資料外洩。建議先修正版本命名一致性與過濾條件完整性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/admin-x-framework/src/utils/stats-config.ts:18` | 版本前綴邏輯與後端不一致，導致端點名稱錯誤 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:85` | session 屬性過濾條件不完整，可能導致資料外洩 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/stats/ContentStatsService.js:102` | 移除 source 參數傳遞可能破壞現有功能 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:10` | 缺少對 `date_from` 和 `date_to` 的驗證可能導致錯誤 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/admin-x-framework/src/utils/stats-config.ts:18</code> 版本前綴邏輯與後端不一致，導致端點名稱錯誤</summary>

此處使用 `config.version ? `${config.version}_${endpointName}` : endpointName`，產生如 `v2_api_kpis` 的端點名稱；但後端 `tinybird.js` 使用 `${pipeName}_${version}`，產生 `api_kpis_v2`。兩者不一致，當前端設定 version 時，會呼叫不存在的端點，導致 API 404。

建議統一命名規則，例如都使用後綴方式，或在此處改為 `${endpointName}_${config.version}`。

**判斷依據**：diff 中新增的這一行，與 `ghost/core/core/server/services/stats/utils/tinybird.js` 中的 `const pipeUrl = version ? `/v0/pipes/${pipeName}_${version}.json` : ...` 形成對比。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:85</code> session 屬性過濾條件不完整，可能導致資料外洩</summary>

在 `sessions_filtered_by_session_attributes` 節點中，只對 `source`、`device`、`utm_source`、`utm_medium`、`utm_campaign`、`utm_term`、`utm_content` 進行過濾，但缺少對 `utm_content` 的過濾條件（實際上已包含，但需確認是否所有 UTM 參數都涵蓋）。若呼叫端傳入未處理的參數，可能導致不正確的資料被回傳。

建議補齊所有 UTM 參數的過濾條件，或明確列出支援的參數並忽略其他。

**判斷依據**：diff 中該行顯示僅有 utm_content 的過濾，但其他 UTM 參數（如 utm_term）也有類似條件，需確認是否遺漏。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/stats/ContentStatsService.js:102</code> 移除 source 參數傳遞可能破壞現有功能</summary>

此處刪除了將 `options.source` 加入 `tinybirdOptions` 的程式碼，但 `source` 是有效的過濾參數，且在其他端點（如 `api_top_sources_v2`）中仍被使用。若呼叫端仍傳入 `source`，將被忽略，導致結果不正確。

建議保留此參數傳遞，或確認所有呼叫端都已更新。

**判斷依據**：diff 中刪除了這幾行，但未在其他地方補上。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:10</code> 缺少對 `date_from` 和 `date_to` 的驗證可能導致錯誤</summary>

在 `timeseries` 節點中，若 `date_from` 大於 `date_to`，會產生空結果或錯誤。建議加入驗證或交換邏輯。

**判斷依據**：diff 中未見對日期範圍的檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 39235 (cache hit 39168) ｜ completion tokens 1212 ｜ PR #13</sub>