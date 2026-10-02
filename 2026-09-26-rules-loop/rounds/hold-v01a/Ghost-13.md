<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Tinybird v2 端點與 materialized view，並將版本控制從 query parameter 改為 config 中的 version 屬性。主要風險在於 `stats-config.ts` 中版本前綴的組合方式與 `tinybird.js` 的命名模式不一致，可能導致端點名稱錯誤；另外 `filtered_sessions_v2.pipe` 的 session 屬性過濾節點缺少 `TYPE` 宣告，可能造成 Tinybird 部署失敗。建議先修正這兩個問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/admin-x-framework/src/utils/stats-config.ts:18` | 版本前綴組合方式與後端不一致，導致端點名稱錯誤 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:85` | Pipe 缺少 TYPE 宣告，可能導致部署失敗 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/admin-x-framework/src/utils/stats-config.ts:18</code> 版本前綴組合方式與後端不一致，導致端點名稱錯誤</summary>

此處將 `config.version` 直接加在 `endpointName` 前面，形成 `v2_api_kpis`；但後端 `tinybird.js` 是將版本加在後面，形成 `api_kpis_v2`。當前端設定 `version: 'v2'` 時，會呼叫不存在的端點 `v2_api_kpis`，造成 404。

建議改為與後端一致的後綴方式：
```ts
const finalEndpointName = config.version ? `${endpointName}_${config.version}` : endpointName;
```

**判斷依據**：diff 中新增的這一行使用 `${config.version}_${endpointName}`，而 `tinybird.js` 使用 `${pipeName}_${version}`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/pipes/filtered_sessions_v2.pipe:85</code> Pipe 缺少 TYPE 宣告，可能導致部署失敗</summary>

此 pipe 檔案結尾沒有 `TYPE` 宣告（例如 `TYPE endpoint` 或 `TYPE materialized`）。Tinybird 通常要求 pipe 檔案明確指定類型，否則部署可能失敗或行為不正確。

請在檔案最後加上適當的 `TYPE` 宣告，例如 `TYPE endpoint`。

**判斷依據**：diff 顯示此檔案最後一行是 utm_content 的條件，沒有 `TYPE` 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 39235 (cache hit 36864) ｜ completion tokens 643 ｜ PR #13</sub>