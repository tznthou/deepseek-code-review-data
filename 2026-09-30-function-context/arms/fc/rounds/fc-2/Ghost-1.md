<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，包含刪除服務檔案、測試、設定，並調整 boot.js 的初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式改變（移除了原本傳入的 `apiUrl` 參數），可能導致排程服務無法正確取得 API URL，進而影響排程功能。另外，`emailAddressService.init()` 的呼叫位置從 `Promise.all` 外移至內部，需確認其相依性是否仍正確。整體而言，移除 xmlrpc 服務本身是合理的，但需確保相關初始化變更不會引入回歸。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫缺少 apiUrl 參數 | 0.80 |
| 🔸 | Minor | `ghost/core/core/boot.js:352` | emailAddressService.init() 移至 Promise.all 內可能影響相依性 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫缺少 apiUrl 參數</summary>

原本 `scheduling.init()` 會傳入 `apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)`，但此 PR 移除了該參數。若 `scheduling` 服務依賴此參數來建構 API 端點，移除後可能導致排程功能失效或產生錯誤。請確認 `scheduling.init()` 是否已改為從其他來源取得 API URL，或此參數已不再需要。

**判斷依據**：diff 中原本的 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`，且未見其他替代設定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 移至 Promise.all 內可能影響相依性</summary>

原本 `emailAddressService.init()` 在 `Promise.all` 之前單獨 await，現在移入 `Promise.all` 陣列中。若其他服務（如 newsletter 或 email service）依賴 emailAddressService 初始化完成，此變更可能導致初始化順序不正確。請確認 emailAddressService 的初始化是否必須在其他服務之前完成。

**判斷依據**：diff 中原本的 `await emailAddressService.init(),` 被移除，並在 `Promise.all` 陣列中加入 `emailAddressService.init(),`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6292 (cache hit 6272) ｜ completion tokens 608 ｜ PR #1</sub>