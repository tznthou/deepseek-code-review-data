<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，並調整了 boot.js 中的服務初始化流程。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式變更，可能導致排程服務無法取得正確的 API URL；此外，移除 `slack.listen()` 可能影響 Slack 整合功能。整體而言，移除 xmlrpc 服務本身是合理的，但需確認相關依賴與初始化順序的正確性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:351` | 移除 slack.listen() 可能導致 Slack 通知功能失效 | 0.70 |
| 🔸 | Minor | `ghost/core/core/boot.js:352` | emailAddressService.init() 移至 Promise.all 可能改變初始化時序 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失</summary>

原本 `scheduling.init()` 會傳入 `{apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)}`，但修改後改為不帶參數呼叫。若 `scheduling.init()` 依賴此參數來設定內部 API 端點，移除後可能導致排程服務無法正確呼叫 API，進而影響排程任務（例如發佈文章）的執行。建議確認 `scheduling.init()` 的實作是否已改為從其他來源取得 API URL，或此參數已不再需要。

**判斷依據**：diff 中 `-        scheduling.init({
-            apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)
-        }),
+        scheduling.init(),`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:351</code> 移除 slack.listen() 可能導致 Slack 通知功能失效</summary>

原本在 `Promise.all` 中有 `slack.listen()`，但修改後被移除。若 Slack 服務需要透過 `listen()` 來註冊事件監聽器以發送通知，移除後將導致 Slack 整合功能無法運作。建議確認 Slack 服務是否已改為其他初始化方式，或此功能已不再需要。

**判斷依據**：diff 中 `-        slack.listen(),` 被移除

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 移至 Promise.all 可能改變初始化時序</summary>

原本 `emailAddressService.init()` 是單獨 await，現在被移入 `Promise.all` 中。若其他服務依賴 emailAddressService 初始化完成後才能執行，此變更可能導致競態條件。建議確認 emailAddressService 的初始化是否為其他服務的前置條件。

**判斷依據**：diff 中 `-    await emailAddressService.init(),
 
     await Promise.all([
+        emailAddressService.init(),`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8104 (cache hit 5760) ｜ completion tokens 747 ｜ PR #1</sub>