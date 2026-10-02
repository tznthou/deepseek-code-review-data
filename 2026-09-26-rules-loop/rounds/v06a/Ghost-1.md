<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，包含刪除服務檔案、測試、設定，並調整 boot.js 中的初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式改變，可能導致排程服務無法取得正確的 API URL；另外移除 `slack.listen()` 可能影響 Slack 整合功能。整體而言，移除 xmlrpc 的變更本身合理，但需確認其他服務的初始化順序與參數傳遞是否正確。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:364` | 移除 slack.listen() 可能導致 Slack 整合失效 | 0.70 |
| 🔸 | Minor | `ghost/core/core/boot.js:313` | 新增註解可能誤導依賴管理方式 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失</summary>

原本 `scheduling.init()` 傳入 `{apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)}`，現在改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確呼叫管理 API，造成排程任務失敗。請確認 `scheduling.init()` 的實作是否已改為從其他來源取得 API URL，或此變更是否為預期行為。

**判斷依據**：diff 中 `-        scheduling.init({
-            apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)
-        }),
+        scheduling.init(),`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:364</code> 移除 slack.listen() 可能導致 Slack 整合失效</summary>

原本在 Promise.all 中有 `slack.listen()`，現在被移除。若 Slack 服務需要透過 `listen()` 註冊事件監聽器來處理通知，移除後將無法接收相關事件，導致 Slack 整合功能失效。請確認 Slack 服務是否已改為其他初始化方式，或此移除是否為預期行為。

**判斷依據**：diff 中 `-        slack.listen(),` 被移除，且未在其他地方新增 slack.listen() 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:313</code> 新增註解可能誤導依賴管理方式</summary>

新增的註解 `// NOTE: If you need to add dependencies for services, use npm install <package>` 可能與專案使用的套件管理器不符。根據規範 R23，此專案應使用 Yarn v1，而非 npm。此註解可能誤導開發者使用錯誤的套件管理器，建議改為 `yarn add` 或移除。

**判斷依據**：diff 中新增的註解行，且規範 R23 要求使用 Yarn。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8094 (cache hit 5760) ｜ completion tokens 770 ｜ PR #1</sub>