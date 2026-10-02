<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Tinybird v2 管線與 materialized view，並將版本控制從 query parameter 改為 config 中的 version 前綴。主要風險在於 `getStatEndpointUrl` 的版本前綴邏輯與 `tinybird.js` 的 URL 建構方式不一致，可能導致前端與後端呼叫不同的端點；此外 `filtered_sessions_v2.pipe` 的 session 屬性過濾條件未正確套用，可能回傳不符合篩選條件的 session。建議先修正這兩個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/admin-x-framework/src/utils/stats-config.ts:18` | 版本前綴順序與後端不一致 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:44` | session 屬性過濾條件未套用 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/stats/ContentStatsService.js:102` | 移除 source 參數傳遞可能影響現有功能 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/admin-x-framework/src/utils/stats-config.ts:18</code> 版本前綴順序與後端不一致</summary>

前端 `getStatEndpointUrl` 將 `config.version` 放在 endpointName 之前（`${config.version}_${endpointName}`），但後端 `tinybird.js` 是放在之後（`${pipeName}_${version}`）。例如 version='v2'、endpointName='api_kpis' 時，前端會呼叫 `v2_api_kpis`，後端會呼叫 `api_kpis_v2`，導致 404。請統一為後端的 `api_kpis_v2` 格式。

**判斷依據**：diff 中新增的這一行，與 `ghost/core/core/server/services/stats/utils/tinybird.js` 中的 `const pipeUrl = version ? `/v0/pipes/${pipeName}_${version}.json` : ...` 直接衝突。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:44</code> session 屬性過濾條件未套用</summary>

在 `sessions_filtered_by_session_attributes` 節點中，雖然從 `_mv_session_data_v2` 選取了 `source`、`device`、`utm_*` 等欄位，但 WHERE 子句中的過濾條件（例如 `{% if defined(source) %} and source = ...`）是放在子查詢外部，且子查詢沒有別名，導致這些條件無法正確引用子查詢中的欄位。這會使 session 屬性過濾失效，回傳不符合條件的 session。請將這些條件移到子查詢內部，或為子查詢加上別名並在外部引用。

**判斷依據**：在 WHERE 子句中直接使用 `source`、`device` 等欄位，但這些欄位只存在於子查詢 `sd` 中，外部查詢無法直接引用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/stats/ContentStatsService.js:102</code> 移除 source 參數傳遞可能影響現有功能</summary>

原本有將 `options.source` 加入 tinybirdOptions 的邏輯（允許空字串代表 Direct traffic），但此 PR 移除了該區塊。若前端仍會傳送 `source` 參數，則後端將不再將其傳遞給 Tinybird，可能導致 source 過濾失效。請確認是否有其他地方處理 source，或是有意移除。

**判斷依據**：diff 中刪除了這段程式碼，但未見其他替代處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36926 (cache hit 1536) ｜ completion tokens 1667 ｜ PR #13</sub>