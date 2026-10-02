<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，並調整了 boot.js 中的服務初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式改變，可能導致排程服務無法取得正確的 API URL，進而影響排程功能。另外，移除 `slack.listen()` 可能導致 Slack 通知功能失效，需確認是否為預期變更。整體而言，變更範圍集中，但需驗證排程與 Slack 服務的初始化行為。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫方式變更可能導致排程服務無法取得正確 API URL | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:364` | 移除 slack.listen() 可能導致 Slack 通知功能失效 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫方式變更可能導致排程服務無法取得正確 API URL</summary>

原本 `scheduling.init()` 傳入 `{apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)}`，現在改為無參數呼叫。若 `scheduling.init()` 依賴此參數來設定 API 端點，移除後可能導致排程服務使用錯誤的 URL 或無法正常運作。請確認 `scheduling.init()` 的實作是否已改為自行取得 URL，或此變更是否為預期行為。

**判斷依據**：diff 中 `-        scheduling.init({
-            apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)
-        }),
+        scheduling.init(),`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:364</code> 移除 slack.listen() 可能導致 Slack 通知功能失效</summary>

原本在 Promise.all 中有 `slack.listen()`，現在被移除。若 Slack 服務需要呼叫 `listen()` 來註冊事件監聽器，移除後將無法接收通知。請確認 Slack 服務是否已改為自動初始化，或此移除是否為預期。

**判斷依據**：diff 中 `-        slack.listen(),` 被移除，且未見替代呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8114 (cache hit 8064) ｜ completion tokens 552 ｜ PR #1</sub>