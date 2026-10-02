<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 XML-RPC ping 服務（xmlrpc.js 及其測試），並從 boot.js 中移除相關初始化與監聽呼叫。同時調整了 emailAddressService.init() 的呼叫位置，並移除了 scheduling.init() 的 apiUrl 參數。主要風險在於 boot.js 中非同步初始化順序的變更可能影響相依服務，以及移除 scheduling.init() 參數可能導致排程功能異常。建議確認 emailAddressService 與其他服務的相依性，並驗證 scheduling 服務在無 apiUrl 參數下的行為。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:352` | emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 移除 apiUrl 參數可能導致排程功能異常 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題</summary>

原本 `await emailAddressService.init()` 是依序執行，現在改為在 `Promise.all` 中並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 完成初始化，可能導致競態條件或初始化失敗。建議確認相依性，必要時保留依序 await。

**判斷依據**：diff 中將原本獨立的 `await emailAddressService.init(),` 移除，並在 `Promise.all` 陣列中加入 `emailAddressService.init(),`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 移除 apiUrl 參數可能導致排程功能異常</summary>

原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

**判斷依據**：diff 中將 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 改為 `scheduling.init()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5795 (cache hit 1536) ｜ completion tokens 576 ｜ PR #1</sub>