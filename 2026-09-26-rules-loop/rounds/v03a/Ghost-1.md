<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 XML-RPC ping 服務（xmlrpc.js 及其測試），並在 boot.js 中移除了相關初始化與依賴。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式變更：原本傳入 `apiUrl` 參數，現在改為無參數呼叫，可能導致排程服務使用錯誤的 API URL。此外，移除 `slack.listen()` 可能影響 Slack 整合功能。整體而言，移除 XML-RPC 服務本身是合理的，但需確認其他服務的初始化變更不會造成回歸。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫缺少 apiUrl 參數可能導致排程服務使用錯誤的 API URL | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:364` | 移除 slack.listen() 可能導致 Slack 整合功能失效 | 0.70 |
| 🔸 | Minor | `ghost/core/core/boot.js:313` | 新增的註解可能誤導依賴管理方式 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫缺少 apiUrl 參數可能導致排程服務使用錯誤的 API URL</summary>

在 boot.js 中，原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`。如果 scheduling 服務依賴 apiUrl 來建構正確的 API 端點，移除該參數可能導致排程任務呼叫錯誤的 URL，進而影響文章排程發佈等功能。建議確認 scheduling.init() 的實作是否已改為自行取得 apiUrl，否則應保留原本的參數傳遞。

**判斷依據**：diff 中顯示原本的 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`，且未在其他地方補上 apiUrl 設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:364</code> 移除 slack.listen() 可能導致 Slack 整合功能失效</summary>

原本在 Promise.all 中有 `slack.listen()`，現在被移除。如果 Slack 服務需要透過 listen() 來註冊事件監聽器，移除後可能導致 Slack 通知功能無法運作。請確認 Slack 服務是否已改為其他初始化方式，否則應保留此呼叫。

**判斷依據**：diff 中顯示 `slack.listen()` 從 Promise.all 陣列中被移除，且未在其他地方新增對應的初始化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:313</code> 新增的註解可能誤導依賴管理方式</summary>

新增的註解 `// NOTE: If you need to add dependencies for services, use npm install <package>` 可能與專案使用 Yarn 的慣例不符（規範 R23）。雖然只是註解，但可能誤導開發者使用 npm 而非 yarn。建議改為 `yarn add <package>` 或移除。

**判斷依據**：diff 中新增了此註解，而專案規範 R23 明確要求使用 Yarn。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8114 (cache hit 5760) ｜ completion tokens 795 ｜ PR #1</sub>