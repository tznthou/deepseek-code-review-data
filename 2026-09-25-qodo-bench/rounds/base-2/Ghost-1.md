<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，包含刪除服務檔案、測試、設定，並調整 boot.js 中的初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式改變，可能導致排程服務無法取得正確的 API URL；另外 `emailAddressService.init()` 從同步呼叫改為 Promise.all 內的非同步呼叫，需確認其初始化順序與相依性。整體而言，移除 xmlrpc 服務本身是合理的，但需確保相關設定與相依套件已一併清理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失 | 0.80 |
| 🔸 | Minor | `ghost/core/core/boot.js:352` | emailAddressService.init() 改為非同步呼叫可能影響相依服務初始化 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失</summary>

原本 `scheduling.init()` 會傳入 `apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)`，現在改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確呼叫 API。請確認 `scheduling.init()` 的實作是否已改為自行取得 URL，或此變更是否為預期行為。

**判斷依據**：diff 中 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`，且未見其他補償設定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 改為非同步呼叫可能影響相依服務初始化</summary>

原本 `await emailAddressService.init()` 是同步等待完成，現在改為在 `Promise.all` 中與其他服務並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 初始化完成，可能導致競態。請確認這些服務的初始化是否已處理相依性，或此變更是否安全。

**判斷依據**：diff 中原本獨立的 `await emailAddressService.init(),` 被移入 `Promise.all` 陣列中。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5795 (cache hit 5760) ｜ completion tokens 583 ｜ PR #1</sub>