<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Tinybird v2 端點與 materialized view，並將版本控制從 request 參數移至 config。主要風險在於 `getStatEndpointUrl` 的版本前綴邏輯與後端 `buildRequest` 的命名不一致，可能導致前端呼叫錯誤的 pipe；另外 `filtered_sessions_v2.pipe` 缺少 `TYPE ENDPOINT` 宣告，可能造成部署或執行問題。建議先修正命名一致性與 pipe 完整性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/admin-x-framework/src/utils/stats-config.ts:18` | 版本前綴邏輯與後端不一致 | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:85` | 缺少 TYPE ENDPOINT 宣告 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>apps/admin-x-framework/src/utils/stats-config.ts:18</code> 版本前綴邏輯與後端不一致</summary>

此處將 `config.version` 直接加在 endpointName 前面（例如 `v2_api_kpis`），但後端 `buildRequest` 是加在後面（`api_kpis_v2`）。若前端使用此函式產生的 URL，將呼叫不存在的 pipe，導致 API 錯誤。建議統一命名規則，例如改為 `${endpointName}_${config.version}`。

**判斷依據**：diff 中新增的這一行，與 `ghost/core/core/server/services/stats/utils/tinybird.js` 中 `const pipeUrl = version ? `/v0/pipes/${pipeName}_${version}.json` : ...` 的命名方式相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:85</code> 缺少 TYPE ENDPOINT 宣告</summary>

此 pipe 檔案結尾沒有 `TYPE ENDPOINT`，而其他 endpoint pipe 都有。這可能導致 Tinybird 無法正確部署或執行此 pipe，進而使所有依賴 `filtered_sessions_v2` 的 v2 端點失效。建議在檔案最後加上 `TYPE ENDPOINT`。

**判斷依據**：diff 中此檔案的最後一行，與其他 endpoint pipe（如 `api_kpis_v2.pipe`）的結尾 `TYPE ENDPOINT` 不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 44982 (cache hit 1536) ｜ completion tokens 615 ｜ PR #13</sub>