<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Tinybird v2 管線與 materialized view，並調整前端與後端的版本選擇機制。主要風險在於 `getStatEndpointUrl` 的版本前綴邏輯與 `tinybird.js` 的後綴邏輯不一致，可能導致前端呼叫錯誤端點；此外，移除 `source` 參數傳遞可能造成功能回歸。建議先修正版本命名一致性，並確認 `source` 過濾是否仍被支援。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/admin-x-framework/src/utils/stats-config.ts:18` | 版本前綴與後端後綴不一致 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/stats/ContentStatsService.js:102` | 移除 source 參數傳遞可能導致功能回歸 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:1` | 新管線缺少 TOKEN 定義 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/admin-x-framework/src/utils/stats-config.ts:18</code> 版本前綴與後端後綴不一致</summary>

前端 `getStatEndpointUrl` 將 `config.version` 加在端點名稱**前面**（例如 `v2_api_kpis`），但後端 `tinybird.js` 是加在**後面**（`api_kpis_v2`）。這會導致前端在設定 `version: 'v2'` 時呼叫不存在的端點，造成 404。

建議統一命名規則，例如都使用後綴 `_v2`。

**判斷依據**：diff 中 `apps/admin-x-framework/src/utils/stats-config.ts` 第 19 行使用前綴，而 `ghost/core/core/server/services/stats/utils/tinybird.js` 第 38 行使用後綴。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/stats/ContentStatsService.js:102</code> 移除 source 參數傳遞可能導致功能回歸</summary>

原本會將 `options.source` 傳遞給 Tinybird 查詢，但此 PR 移除了該區塊。若前端仍會傳送 `source` 過濾條件，這些條件將被忽略，導致統計結果不正確。

請確認 `source` 過濾是否已不再需要，或改由其他機制處理；若仍需要，應保留傳遞邏輯。

**判斷依據**：diff 中 `ghost/core/core/server/services/stats/ContentStatsService.js` 刪除了上述程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:1</code> 新管線缺少 TOKEN 定義</summary>

此管線檔案開頭沒有 `TOKEN` 宣告，而其他 v2 管線（如 `api_active_visitors_v2.pipe`）都有。若 Tinybird 要求每個 pipe 必須定義 token，此管線可能無法部署或執行。

請確認是否為刻意省略，或補上必要的 token 宣告。

**判斷依據**：diff 中 `api_kpis_v2.pipe` 開頭缺少 TOKEN 行，而其他新增的 v2 pipe 都有。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36890 (cache hit 1408) ｜ completion tokens 859 ｜ PR #13</sub>