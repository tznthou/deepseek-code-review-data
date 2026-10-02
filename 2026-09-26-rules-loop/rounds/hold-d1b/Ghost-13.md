<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 新增 Tinybird v2 管線與 materialized view，並調整 stats 設定以支援版本後綴。主要風險在於移除 `tb_version` 參數與 `source` 過濾條件可能造成 API 相容性問題，以及新管線中 session 資料的 join 邏輯可能導致資料重複計算。建議先確認這些變更是否為預期行為，並補齊對應的測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/stats/ContentStatsService.js:102` | 移除 source 過濾條件可能破壞現有 API 行為 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:93` | session_metrics 與 filtered_sessions_v2 的 join 可能造成重複計算 | 0.75 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_devices_v2.pipe:10` | session_data 節點未使用 -Merge 函數讀取 AggregatingMergeTree | 0.60 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe:19` | member_status 過濾條件可能包含重複的 'comped' | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/stats/ContentStatsService.js:102</code> 移除 source 過濾條件可能破壞現有 API 行為</summary>

原本的程式碼會將 `options.source` 加入 Tinybird 查詢參數，但這次改動移除了這個區塊。如果前端或其他服務仍會傳送 `source` 參數，這些請求將不再被過濾，導致回傳未過濾的資料。請確認是否有其他地方處理 `source`，或這是否為預期的行為變更。

**判斷依據**：diff 中移除了上述程式碼區塊，且未見其他替代處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:93</code> session_metrics 與 filtered_sessions_v2 的 join 可能造成重複計算</summary>

在 `session_metrics` 節點中，`session_data` 與 `filtered_sessions_v2` 以 `session_id` 進行 inner join。若 `filtered_sessions_v2` 因 hit-level 過濾條件而對同一 session 回傳多筆資料（例如同 session 內有多個符合條件的 hit），則 join 後會產生重複的 session 資料，導致 `visits`、`pageviews` 等指標被高估。建議確認 `filtered_sessions_v2` 是否保證每個 session 只回傳一筆，或改用 `distinct` 或聚合方式處理。

**判斷依據**：diff 中 `filtered_sessions_v2.pipe` 的 `sessions_filtered_by_hit_attributes` 節點使用 `select distinct session_id`，但若同一 session 有多個 hit 符合條件，仍可能回傳多筆相同 session_id。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_devices_v2.pipe:10</code> session_data 節點未使用 -Merge 函數讀取 AggregatingMergeTree</summary>

在 `api_top_devices_v2.pipe` 的 `session_data` 節點中，直接從 `_mv_session_data_v2` 選取 `argMinMerge(device)`，但未先使用 `-Merge` 函數（如 `argMinMerge` 本身即為 merge 函數，但需確認資料表引擎為 AggregatingMergeTree 且查詢時需使用 `-Merge` 後綴）。若直接查詢底層表，可能無法正確合併多個 part 的聚合狀態。建議確認 Tinybird 的 materialized view 查詢方式，或參考其他 v2 管線的寫法。

**判斷依據**：diff 中其他管線（如 `api_kpis_v2.pipe`）使用 `countMerge`、`minMerge` 等函數，但未見明確的 `-Merge` 表名後綴。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe:19</code> member_status 過濾條件可能包含重複的 'comped'</summary>

在 `api_top_locations_v2.pipe` 的 `_top_locations_0` 節點中，`member_status` 的過濾條件使用 `|| if('paid' IN {{ Array(member_status) }}, ['comped'], [])`。若 `member_status` 陣列中已包含 `'comped'`，則會產生重複值，可能影響查詢結果。建議確認此邏輯是否為預期，或改用 `arrayDistinct` 等方式處理。

**判斷依據**：diff 中該條件在多個管線中重複出現，且未見去重處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 39272 (cache hit 39168) ｜ completion tokens 1283 ｜ PR #13</sub>