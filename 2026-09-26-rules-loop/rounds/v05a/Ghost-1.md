<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 XML-RPC ping 服務（xmlrpc.js 及其測試），並在 boot.js 中移除了相關初始化呼叫。同時調整了 emailAddressService.init() 的呼叫位置，並移除了 scheduling.init() 的參數。主要風險在於移除服務後是否有其他程式碼仍依賴它，以及 boot.js 中非同步初始化順序的變更是否會造成競態。整體而言，移除本身是合理的，但需確認沒有殘留引用。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:352` | emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題 | 0.80 |
| 🔸 | Minor | `ghost/core/core/boot.js:368` | scheduling.init() 移除 apiUrl 參數可能影響排程功能 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題</summary>

原本 `emailAddressService.init()` 在 `Promise.all` 之前單獨 await，現在移入 `Promise.all` 陣列中。如果其他服務（如 newsletter service 或 email service）依賴 emailAddressService 初始化完成，則可能因為並行執行而導致依賴服務在 emailAddressService 尚未就緒時就嘗試使用其功能。

建議確認 emailAddressService 的初始化是否為其他服務的前置條件，若是，則應保持單獨 await 或使用 `Promise.all` 前先 await。

**判斷依據**：diff 中原本 `await emailAddressService.init(),` 被移除，並在 `Promise.all` 陣列中加入 `emailAddressService.init(),`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 移除 apiUrl 參數可能影響排程功能</summary>

原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 apiUrl，現在改為無參數呼叫。若 scheduling 服務需要 apiUrl 來建構 API 端點，移除後可能導致排程任務無法正確運作。

請確認 scheduling.init() 是否已改為從其他來源取得 apiUrl，或此參數已不再需要。

**判斷依據**：diff 中原本的 `scheduling.init({ apiUrl: ... })` 被改為 `scheduling.init()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8028 (cache hit 5760) ｜ completion tokens 593 ｜ PR #1</sub>