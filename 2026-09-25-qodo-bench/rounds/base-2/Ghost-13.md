<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Tinybird v2 端點與 materialized view，並將版本控制從 request 參數改為 config 設定。主要風險在於 `stats-config.ts` 中版本前綴的組合方式與後端 `tinybird.js` 不一致，可能導致端點名稱錯誤；另外移除 `source` 參數傳遞可能造成既有功能回歸。建議先修正版本命名邏輯並確認 source 過濾需求。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/admin-x-framework/src/utils/stats-config.ts:18` | 版本前綴組合方式與後端不一致 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/stats/ContentStatsService.js:105` | 移除 source 參數傳遞可能造成功能回歸 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:1` | v2 端點缺少 TOKEN 定義 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/admin-x-framework/src/utils/stats-config.ts:18</code> 版本前綴組合方式與後端不一致</summary>

前端將 `config.version` 直接加在 `endpointName` 前面（`${config.version}_${endpointName}`），但後端 `tinybird.js` 是加在後面（`${pipeName}_${version}`）。若同時使用前端與後端，會產生不同的端點名稱（例如前端 `v2_api_kpis` vs 後端 `api_kpis_v2`），導致請求失敗。

建議統一命名規則，例如都使用後綴方式。

**判斷依據**：diff 中新增的這一行與 `ghost/core/core/server/services/stats/utils/tinybird.js` 中的 `const pipeUrl = version ? `/v0/pipes/${pipeName}_${version}.json` : ...` 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/stats/ContentStatsService.js:105</code> 移除 source 參數傳遞可能造成功能回歸</summary>

原本會將 `options.source` 加入 Tinybird 查詢參數，但此 PR 移除了該邏輯。若前端或其他呼叫端仍會傳入 `source` 參數，將無法過濾來源，導致統計資料不正確。

請確認是否刻意移除，或應保留此功能。

**判斷依據**：diff 中刪除了這幾行，且沒有在其他地方補上對應的處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_kpis_v2.pipe:1</code> v2 端點缺少 TOKEN 定義</summary>

新建立的 v2 端點檔案（如 `api_kpis_v2.pipe`）開頭沒有 `TOKEN` 宣告，但其他端點（如 `api_active_visitors_v2.pipe`）有。若 Tinybird 要求每個 pipe 都需定義 token，這些端點可能無法部署或存取。

請確認是否為刻意省略，或需補上。

**判斷依據**：diff 中 `api_kpis_v2.pipe` 的開頭直接是 `NODE timeseries`，沒有 TOKEN 行，而其他 v2 端點檔案有。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36926 (cache hit 36864) ｜ completion tokens 852 ｜ PR #13</sub>