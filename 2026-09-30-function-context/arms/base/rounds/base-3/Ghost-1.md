<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，包含刪除服務檔案、測試、設定檔中的 useRpcPing 選項，並調整 boot.js 中的初始化流程。主要風險在於 boot.js 中對 emailAddressService.init() 的呼叫方式改變，以及 scheduling.init() 的參數移除，可能影響相關服務的初始化行為。整體而言，移除 xmlrpc 服務本身是合理的，但需確認其他服務的初始化順序與參數變更不會造成回歸。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:352` | emailAddressService.init() 從同步呼叫改為 Promise.all 內的非同步呼叫，可能影響依賴它的服務初始化順序 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 移除了 apiUrl 參數，可能導致排程服務無法正確建構 API URL | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 從同步呼叫改為 Promise.all 內的非同步呼叫，可能影響依賴它的服務初始化順序</summary>

原本 `await emailAddressService.init()` 是同步等待完成後才進行後續的 Promise.all，現在改成在 Promise.all 內與其他服務並行初始化。如果其他服務（如 newsletter service 或 email service）依賴 emailAddressService 初始化完成，可能會因為並行執行而產生競態條件。建議確認這些服務的依賴關係，若有必要，應保留 emailAddressService.init() 的 await 順序，或將依賴它的服務也放入同一個 Promise.all 中並確保順序。

**判斷依據**：diff 中將原本的 `await emailAddressService.init(),` 移除，並在 Promise.all 陣列中加入 `emailAddressService.init(),`，且註解提到 newsletter service 和 email service 依賴 email address service。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 移除了 apiUrl 參數，可能導致排程服務無法正確建構 API URL</summary>

原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入了動態產生的 API URL，現在改成無參數呼叫。如果 scheduling 服務內部需要這個 URL 來進行 API 呼叫，移除後可能導致功能失效或使用錯誤的 URL。建議確認 scheduling.init() 的實作是否已改為自行取得 URL，或是否應保留此參數。

**判斷依據**：diff 中刪除了原本的 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })`，改為 `scheduling.init()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5795 (cache hit 5760) ｜ completion tokens 647 ｜ PR #1</sub>