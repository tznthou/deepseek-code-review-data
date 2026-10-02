<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Tinybird v2 端點與 materialized view，並將版本控制從 per-request 的 tbVersion 改為 config 層級的 version。主要風險在於：1) 移除 source 參數傳遞可能導致既有過濾失效；2) 新 SQL 中多處使用未定義的 filtered_sessions_v2 節點，可能造成查詢失敗；3) 版本字串直接拼接進 URL，若 config 未受控可能造成路徑操作。建議先確認 filtered_sessions_v2 的定義與 source 過濾的相容性。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/stats/ContentStatsService.js:100` | 移除 source 參數傳遞可能導致過濾失效 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:93` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_top_devices_v2.pipe:21` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe:11` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_top_pages_v2.pipe:12` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_top_sources_v2.pipe:21` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_campaigns_v2.pipe:21` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_contents_v2.pipe:21` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_mediums_v2.pipe:21` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_sources_v2.pipe:21` | 引用未定義的 filtered_sessions_v2 節點 | 0.85 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/stats/ContentStatsService.js:100</code> 移除 source 參數傳遞可能導致過濾失效</summary>

在 fetchRawTopContentData 中，原本會將 options.source 傳遞給 Tinybird（即使為空字串），但此 PR 移除了該區塊。若前端仍會傳送 source 參數（例如用於「Direct」流量過濾），則此過濾將被忽略，導致回傳未過濾的資料。建議確認 source 參數是否仍被使用，若需要保留過濾功能，應恢復傳遞邏輯。

**判斷依據**：diff 中刪除了上述程式碼區塊，且未在其他地方補上 source 的傳遞。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:93</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 session_metrics 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_kpis_v2.pipe 的 session_metrics 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_devices_v2.pipe:21</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 top_devices 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_top_devices_v2.pipe 的 top_devices 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe:11</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 _top_locations_0 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_top_locations_v2.pipe 的 _top_locations_0 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_pages_v2.pipe:12</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 _top_pages_0 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_top_pages_v2.pipe 的 _top_pages_0 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_sources_v2.pipe:21</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 top_sources 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_top_sources_v2.pipe 的 top_sources 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_utm_campaigns_v2.pipe:21</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 top_utm_campaigns 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_top_utm_campaigns_v2.pipe 的 top_utm_campaigns 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_utm_contents_v2.pipe:21</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 top_utm_contents 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_top_utm_contents_v2.pipe 的 top_utm_contents 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_utm_mediums_v2.pipe:21</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 top_utm_mediums 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_top_utm_mediums_v2.pipe 的 top_utm_mediums 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_utm_sources_v2.pipe:21</code> 引用未定義的 filtered_sessions_v2 節點</summary>

在 top_utm_sources 節點中，SQL 使用了 `inner join filtered_sessions_v2 fs`，但此 pipe 檔案中並未定義名為 filtered_sessions_v2 的節點。這可能導致 Tinybird 在編譯 pipe 時報錯，或查詢時找不到該節點。請確認 filtered_sessions_v2 是否應為外部 pipe 或需在本檔案中定義。

**判斷依據**：diff 中 api_top_utm_sources_v2.pipe 的 top_utm_sources 節點引用了 filtered_sessions_v2，但該 pipe 檔案中沒有此節點定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 44982 (cache hit 44928) ｜ completion tokens 2729 ｜ PR #13</sub>