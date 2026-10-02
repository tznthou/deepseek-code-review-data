<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，包含刪除服務檔案、測試、設定，並調整 boot.js 中的初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式改變，可能影響排程服務的初始化；另外刪除 `slack.listen()` 可能導致 Slack 通知功能失效。整體而言，移除 xmlrpc 是合理的清理，但需確認相關服務的初始化變更是否為預期行為。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫方式變更可能導致排程服務初始化失敗 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:368` | 移除 slack.listen() 可能導致 Slack 通知功能失效 | 0.70 |
| 🔸 | Minor | `ghost/core/core/boot.js:313` | 新增的註解可能誤導開發者使用 npm 而非 yarn | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫方式變更可能導致排程服務初始化失敗</summary>

原本 `scheduling.init()` 傳入 `{apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)}`，現在改為無參數呼叫。若 `scheduling.init()` 依賴 `apiUrl` 參數來設定內部 API 端點，移除後可能導致排程服務無法正常運作（例如無法觸發 webhook 或執行排程任務）。請確認 `scheduling.init()` 的實作是否已改為從其他來源取得 `apiUrl`，或此變更是否為預期行為。

**判斷依據**：diff 中 `-        scheduling.init({
-            apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)
-        }),
+        scheduling.init(),`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> 移除 slack.listen() 可能導致 Slack 通知功能失效</summary>

原本在 `Promise.all` 中有 `slack.listen()`，現在被移除。若 Slack 服務需要透過 `listen()` 註冊事件監聽器來處理通知，移除後將導致 Slack 通知無法發送。請確認 Slack 服務是否已改為其他初始化方式，或此功能是否已棄用。

**判斷依據**：diff 中 `-        slack.listen(),
` 被移除，且未見替代呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:313</code> 新增的註解可能誤導開發者使用 npm 而非 yarn</summary>

新增註解 `// NOTE: If you need to add dependencies for services, use npm install <package>`，但專案規範 R23 要求使用 Yarn v1。此註解可能導致開發者誤用 npm，違反專案慣例。建議改為 `yarn add <package>` 或移除。

**判斷依據**：diff 中新增的註解行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8094 (cache hit 8064) ｜ completion tokens 752 ｜ PR #1</sub>