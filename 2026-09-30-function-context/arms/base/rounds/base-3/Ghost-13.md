<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 Tinybird v2 端點與 materialized view，並將版本選擇從 query parameter 改為 config 中的 `version` 欄位。主要風險在於 `version` 字串直接拼接進 URL 與 pipe 名稱，若未驗證可能導致路徑操縱或呼叫到非預期的端點；此外移除 `tb_version` 參數與 `source` 過濾條件可能造成既有 API 使用者相容性問題。建議先確認 `version` 的來源與驗證方式，並補齊對應的測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/stats/utils/tinybird.js:37` | 未驗證的 version 字串直接拼接進 URL，可能導致路徑操縱 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/stats/ContentStatsService.js:102` | 移除 source 過濾條件可能破壞既有 API 行為 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/api/endpoints/stats.js:125` | 移除 tb_version 參數可能造成 API 相容性問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/stats/utils/tinybird.js:37</code> 未驗證的 version 字串直接拼接進 URL，可能導致路徑操縱</summary>

`version` 來自 `statsConfig?.version`，直接以字串拼接方式插入 URL（`/v0/pipes/${pipeName}_${version}.json`）。若 config 中的 `version` 未經嚴格驗證（例如只允許 `[a-zA-Z0-9_-]+`），攻擊者或錯誤設定可能注入 `../` 等路徑片段，導致請求被導向非預期的 Tinybird pipe，甚至繞過權限控制。建議在 `buildRequest` 中對 `version` 進行正規表示式驗證，或使用 Tinybird 提供的參數化 pipe 名稱機制。

**判斷依據**：diff 中新增的 `version` 直接以字串模板拼接，且未見任何驗證邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/stats/ContentStatsService.js:102</code> 移除 source 過濾條件可能破壞既有 API 行為</summary>

原本 `options.source` 會被加入 tinybirdOptions（即使為空字串），但此 PR 刪除了該區塊。若前端或其他服務依賴 `source` 參數來過濾流量來源，升級後這些請求將不再帶有 `source` 參數，導致回傳未過濾的資料。請確認是否有其他呼叫端仍傳遞 `source`，並評估是否應保留此參數的傳遞。

**判斷依據**：diff 中刪除了處理 `options.source` 的程式碼區塊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/api/endpoints/stats.js:125</code> 移除 tb_version 參數可能造成 API 相容性問題</summary>

從允許的查詢參數清單中移除了 `tb_version`。若外部使用者仍傳送此參數，可能會被忽略或導致驗證錯誤。建議確認此參數是否已完全棄用，並在必要時提供過渡期或文件說明。

**判斷依據**：diff 中刪除了 `'tb_version'` 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36926 (cache hit 36864) ｜ completion tokens 905 ｜ PR #13</sub>