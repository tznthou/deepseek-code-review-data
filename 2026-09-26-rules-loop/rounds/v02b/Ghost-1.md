<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 XML-RPC ping 服務（pingomatic），包括服務檔案、測試、設定與 boot.js 中的初始化。整體方向合理，但 boot.js 中 `scheduling.init()` 的呼叫方式被改為無參數，可能導致排程服務無法取得正確的 API URL，進而影響排程功能。另外，移除 `slack.listen()` 但未移除相關服務初始化，可能造成 Slack 通知失效。建議確認這些變更的意圖與影響。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/boot.js:368` | scheduling.init() 缺少 apiUrl 參數可能導致排程服務無法正常運作 | 0.90 |
| ⚠️ | Major | `ghost/core/core/boot.js:351` | 移除 slack.listen() 但保留 slack 服務初始化可能導致 Slack 通知失效 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 缺少 apiUrl 參數可能導致排程服務無法正常運作</summary>

在 `initServices()` 中，原本 `scheduling.init()` 會傳入 `apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)`，但此 PR 將其改為無參數呼叫。若 `scheduling.init()` 依賴此參數來建構 API 呼叫的 URL，移除後可能導致排程服務無法正確呼叫內部 API，造成排程任務失敗。請確認 `scheduling.init()` 是否有預設值或從其他來源取得 URL，否則應保留此參數。

**判斷依據**：diff 中 `-        scheduling.init({
-            apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)
-        }),
+        scheduling.init(),`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:351</code> 移除 slack.listen() 但保留 slack 服務初始化可能導致 Slack 通知失效</summary>

原本在 `Promise.all` 中有 `slack.listen()`，此 PR 將其移除，但 `slack` 服務仍被初始化（`const slack = require('./server/services/slack');` 且可能在其他地方呼叫 `slack.init()`）。若 `slack.listen()` 是註冊事件監聽器的必要步驟，移除後將導致 Slack 通知功能失效。請確認是否應一併移除 Slack 服務的初始化，或保留 `slack.listen()`。

**判斷依據**：diff 中 `-        slack.listen(),` 被移除，但 `slack` 服務的 require 和初始化仍在。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8104 (cache hit 8064) ｜ completion tokens 616 ｜ PR #1</sub>