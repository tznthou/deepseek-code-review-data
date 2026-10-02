<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 XML-RPC ping 服務（xmlrpc.js 及其測試），並在 boot.js 中調整了服務初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式改變，可能影響排程服務的初始化；另外刪除服務後需確認沒有其他模組仍依賴 xmlrpc。整體變更範圍明確，但需驗證排程服務的初始化參數是否正確。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫方式變更可能導致排程服務初始化失敗 | 0.75 |
| 🔸 | Minor | `ghost/core/core/boot.js:352` | emailAddressService.init() 從同步呼叫改為 Promise.all 內的非同步呼叫 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫方式變更可能導致排程服務初始化失敗</summary>

原本 `scheduling.init()` 會傳入 `apiUrl` 參數，現在改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正常運作。請確認 `scheduling.init()` 的實作是否已改為從其他來源取得 API URL，或此參數已不再需要。

**判斷依據**：diff 中原本的 `scheduling.init({ apiUrl: urlUtils.url('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`，且未見其他補償設定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 從同步呼叫改為 Promise.all 內的非同步呼叫</summary>

原本 `emailAddressService.init()` 是單獨 await，現在被移入 `Promise.all` 陣列中。若 `emailAddressService.init()` 有依賴其他服務先初始化的順序性，此變更可能造成競態。請確認該服務的初始化是否獨立。

**判斷依據**：diff 中原本的 `await emailAddressService.init(),` 被移除，並在 `Promise.all` 陣列中加入 `emailAddressService.init(),`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8028 (cache hit 7936) ｜ completion tokens 544 ｜ PR #1</sub>