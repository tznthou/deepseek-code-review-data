<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，包括服務檔案、測試、設定與 boot.js 中的初始化。整體而言，移除是乾淨的，但 boot.js 中對 emailAddressService.init() 的呼叫方式從原本的逗號分隔改為放入 Promise.all 陣列，此變更可能影響初始化順序或錯誤處理，需確認其意圖。另外，scheduling.init() 的呼叫移除了 apiUrl 參數，需確認 scheduling 服務是否已改為自行取得該值，否則可能導致排程功能失效。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:352` | emailAddressService.init() 呼叫方式變更可能影響初始化順序 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 移除 apiUrl 參數可能導致排程功能異常 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 呼叫方式變更可能影響初始化順序</summary>

原本 `await emailAddressService.init(),` 是單獨的 await 表達式（雖然後面有逗號，但實際上是依序執行），現在改為放入 `Promise.all` 陣列中，與其他服務並行初始化。若 emailAddressService 的初始化有依賴其他服務（如註解所述 newsletter service 和 email service 依賴 email address service），並行初始化可能導致相依性問題。建議確認 emailAddressService.init() 是否必須在其他服務之前完成，若是，則應保持獨立的 await。

**判斷依據**：diff 中原本的 `await emailAddressService.init(),` 被移除，並在 Promise.all 陣列中加入 `emailAddressService.init(),`，改變了執行順序。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 移除 apiUrl 參數可能導致排程功能異常</summary>

原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入了 apiUrl，現在改為 `scheduling.init()`。若 scheduling 服務內部未自行取得 apiUrl，則可能無法正確建構 API 呼叫的 URL，導致排程任務失敗。請確認 scheduling 服務的實作是否已改為從其他來源取得 apiUrl，或此參數已不再需要。

**判斷依據**：diff 中原本的 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`，移除了 apiUrl 參數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5759 (cache hit 5632) ｜ completion tokens 637 ｜ PR #1</sub>