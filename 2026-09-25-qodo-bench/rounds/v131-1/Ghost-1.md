<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 XML-RPC ping 服務（xmlrpc.js）及其相關設定與測試，並調整了 boot.js 中的服務初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式變更，可能導致排程服務無法正確取得 API URL；另外移除了 `slack.listen()` 的呼叫，若 Slack 服務仍需要監聽事件，可能造成功能失效。整體而言，移除 XML-RPC 服務本身是合理的，但需確認其他服務的初始化變更是否為有意為之。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫方式變更可能導致 API URL 遺失 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:368` | 移除 slack.listen() 可能導致 Slack 服務無法接收事件 | 0.70 |
| 🔸 | Minor | `ghost/core/core/boot.js:352` | emailAddressService.init() 移至 Promise.all 可能改變初始化時序 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫方式變更可能導致 API URL 遺失</summary>

原本 `scheduling.init()` 會傳入 `{apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)}`，但修改後改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確運作。請確認 `scheduling.init()` 是否已有其他方式取得 API URL，或此變更是否為有意為之。

**判斷依據**：diff 中原本的 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`，且未見其他替代設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> 移除 slack.listen() 可能導致 Slack 服務無法接收事件</summary>

原本在 `Promise.all` 中有 `slack.listen()`，但修改後被移除。若 Slack 服務需要監聽特定事件（例如發佈通知），移除後可能導致功能失效。請確認 Slack 服務是否已改為其他方式初始化，或此移除是否為有意為之。

**判斷依據**：diff 中原本的 `slack.listen()` 被移除，且未見其他替代呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 移至 Promise.all 可能改變初始化時序</summary>

原本 `emailAddressService.init()` 是單獨 await，現在被移入 `Promise.all` 中。若其他服務依賴 emailAddressService 初始化完成，可能造成競態。請確認此變更不會影響相依服務的初始化順序。

**判斷依據**：diff 中原本的 `await emailAddressService.init(),` 被改為在 `Promise.all` 陣列中的 `emailAddressService.init(),`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5759 (cache hit 1408) ｜ completion tokens 744 ｜ PR #1</sub>