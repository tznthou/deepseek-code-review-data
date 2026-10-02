<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Tinybird v2 管線與 materialized view，並調整前端與後端的版本參數傳遞方式。主要風險在於 `stats-config.ts` 中版本前綴的組合方式與後端 `tinybird.js` 不一致，可能導致呼叫錯誤的管線名稱；另外 `filtered_sessions_v2.pipe` 的 session 屬性過濾條件可能因時區處理不當而漏掉邊界資料。建議先修正版本命名邏輯，並確認時區轉換的正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/admin-x-framework/src/utils/stats-config.ts:18` | 版本前綴組合方式與後端不一致 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:67` | session 屬性過濾的時區處理可能造成邊界資料遺漏 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:100` | `pathname_pageviews` 節點缺少 `site_uuid` 過濾條件 | 0.75 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe:17` | `member_status` 過濾邏輯可能與其他端點不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/admin-x-framework/src/utils/stats-config.ts:18</code> 版本前綴組合方式與後端不一致</summary>

前端將 `config.version` 直接加在 endpointName 前面（例如 `v2_api_kpis`），但後端 `tinybird.js` 是加在後面（`api_kpis_v2`）。這會導致前端呼叫不存在的管線，所有 v2 端點都會失敗。

建議：改為與後端一致的 `${endpointName}_${config.version}`。

**判斷依據**：diff 中新增的這一行，與後端 `tinybird.js` 的 `/v0/pipes/${pipeName}_${version}.json` 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:67</code> session 屬性過濾的時區處理可能造成邊界資料遺漏</summary>

在 `sessions_filtered_by_session_attributes` 節點中，`first_pageview` 是直接從 `_mv_session_data_v2` 取得的 `minMerge(first_pageview)`，其值為 UTC 時間戳。但過濾條件使用 `toDateTime({{ Date(date_from) }}, {{ String(timezone) }})` 將日期轉換為指定時區的 DateTime，兩者比較時可能因時區不同而漏掉邊界上的 session。

建議：先將 `first_pageview` 轉換到目標時區再比較，或統一使用 UTC 進行比較。

**判斷依據**：diff 中該行直接比較 `first_pageview` 與帶時區的 DateTime，未做時區轉換。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:100</code> `pathname_pageviews` 節點缺少 `site_uuid` 過濾條件</summary>

在 `pathname_pageviews` 節點中，查詢 `_mv_hits` 時只透過 `filtered_sessions_v2` 間接過濾 session，但沒有直接加上 `site_uuid` 條件。若 `filtered_sessions_v2` 因某些原因未能正確過濾（例如參數缺失），可能導致跨租戶資料洩漏。

建議：在 `where` 子句中明確加入 `site_uuid = {{ String(site_uuid, ...) }}`。

**判斷依據**：diff 中 `pathname_pageviews` 節點的 `where` 子句沒有 `site_uuid` 條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe:17</code> `member_status` 過濾邏輯可能與其他端點不一致</summary>

在 `api_top_locations_v2.pipe` 中，`member_status` 的過濾條件使用了 `select arrayJoin(...)` 子查詢，而其他端點（如 `api_top_pages_v2.pipe`）直接使用 `IN` 搭配 `Array` 參數。雖然功能可能相同，但風格不一致，且子查詢可能影響效能。

建議：統一使用 `IN` 搭配 `Array` 參數，或確認此寫法為必要。

**判斷依據**：diff 中該端點使用子查詢，而其他端點使用直接 `IN`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36890 (cache hit 36864) ｜ completion tokens 1275 ｜ PR #13</sub>