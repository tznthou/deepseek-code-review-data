<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 新增 Tinybird v2 端點與 materialized view，並調整 stats 設定以支援版本後綴。主要風險在於移除 `tb_version` 參數與 `source` 過濾邏輯，可能造成 API 相容性問題；此外，新增的 Tinybird pipe 檔案使用 2 空格縮排，違反專案規範 R17。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_active_visitors_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_post_visitor_counts_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_devices_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_pages_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_sources_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_campaigns_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_contents_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_mediums_v2.pipe:1` | [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排 | 0.95 |

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_kpis_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_active_visitors_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_active_visitors_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_active_visitors_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_post_visitor_counts_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_post_visitor_counts_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_post_visitor_counts_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_devices_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_top_devices_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_top_devices_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_top_locations_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_top_locations_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_pages_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_top_pages_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_top_pages_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_sources_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_top_sources_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_top_sources_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_utm_campaigns_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_top_utm_campaigns_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_campaigns_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_utm_contents_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_top_utm_contents_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_contents_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_top_utm_mediums_v2.pipe:1</code> [R17] 新增 Tinybird pipe 檔案使用 2 空格縮排</summary>

專案規範 R17 要求所有原始碼檔案使用 4 空格縮排（JSON 和 YAML 除外）。此 PR 新增的 `.pipe` 檔案（如 `api_top_utm_mediums_v2.pipe`）內容使用 2 空格縮排，違反規範。

建議將所有新增的 `.pipe` 檔案內容改為 4 空格縮排。

**判斷依據**：diff 中新增的 `ghost/core/core/server/data/tinybird/endpoints/api_top_utm_mediums_v2.pipe` 檔案內容以 2 空格縮排，例如 `TOKEN "stats_page" READ` 前有 2 空格，而專案規範 R17 要求 4 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 39272 (cache hit 39168) ｜ completion tokens 3038 ｜ PR #13</sub>