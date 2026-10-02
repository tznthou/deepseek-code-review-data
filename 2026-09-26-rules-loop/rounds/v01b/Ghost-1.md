<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，並調整了 boot.js 中的服務初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式變更，可能導致排程服務無法取得正確的 API URL；此外，移除 `slack.listen()` 可能影響 Slack 整合功能。整體而言，移除 xmlrpc 服務本身是合理的，但需確認相關依賴與初始化順序的正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:351` | 移除 slack.listen() 可能導致 Slack 整合失效 | 0.70 |
| 🔸 | Minor | `ghost/core/core/boot.js:352` | emailAddressService.init() 移至 Promise.all 可能改變初始化時序 | 0.60 |
| 🔹 | Nit | `ghost/core/core/boot.js:313` | 新增註解可能不必要 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失</summary>

原本 `scheduling.init()` 會傳入 `{apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)}`，但修改後改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確運作。建議確認 `scheduling.init()` 的實作是否已改為從其他來源取得 API URL，或此變更是否為預期行為。

**判斷依據**：diff 中原本的 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`，且未見其他替代設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:351</code> 移除 slack.listen() 可能導致 Slack 整合失效</summary>

原本在 `Promise.all` 中有 `slack.listen()`，但修改後被移除。若 Slack 服務需要監聽事件（例如發佈通知），移除後可能導致功能失效。請確認 Slack 服務是否已改為其他初始化方式，或此移除是否為預期。

**判斷依據**：diff 中 `slack.listen(),` 被刪除，且未見其他替代呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 移至 Promise.all 可能改變初始化時序</summary>

原本 `emailAddressService.init()` 在 `Promise.all` 之前單獨呼叫，現在移入 `Promise.all` 中。若其他服務依賴 emailAddressService 初始化完成，可能導致競態。建議確認依賴關係是否允許並行初始化。

**判斷依據**：diff 中原本的 `await emailAddressService.init(),` 被移除，並在 `Promise.all` 中加入 `emailAddressService.init(),`。

</details>

<details><summary>🔹 <b>Nit</b> — <code>ghost/core/core/boot.js:313</code> 新增註解可能不必要</summary>

新增的註解 `// NOTE: If you need to add dependencies for services, use npm install <package>` 可能與專案使用 Yarn 的慣例不符（R23）。若專案使用 Yarn，建議改為 `yarn add`。

**判斷依據**：diff 中新增的註解提到 npm install，但專案規範 R23 要求使用 Yarn。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8104 (cache hit 8064) ｜ completion tokens 904 ｜ PR #1</sub>