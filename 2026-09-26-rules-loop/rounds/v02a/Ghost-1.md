<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 xmlrpc/pingomatic ping 服務，包含刪除服務檔案、測試、設定，並調整 boot.js 中的初始化流程。主要風險在於 boot.js 中 `emailAddressService.init()` 的呼叫位置變更，可能造成初始化順序問題；另外 `scheduling.init()` 的參數移除可能影響排程功能。整體而言，移除功能本身是合理的，但需確認相依服務的初始化順序與排程設定。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:352` | emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題 | 0.80 |
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 移除 apiUrl 參數可能影響排程功能 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題</summary>

原本 `emailAddressService.init()` 在 `stripe.init()` 之後立即執行，現在被移入 `Promise.all` 中，與其他服務並行初始化。註解提到 newsletter 和 email service 依賴 email address service，若這些服務在 emailAddressService 尚未完成初始化時就開始執行，可能導致相依性問題。建議確認 emailAddressService 的初始化是否為其他服務的前置條件，若是，應保持順序或使用 await 確保完成。

**判斷依據**：diff 中 `-    await emailAddressService.init(),` 被移除，並在 `Promise.all` 中加入 `+        emailAddressService.init(),`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 移除 apiUrl 參數可能影響排程功能</summary>

原本 `scheduling.init()` 傳入 `apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)`，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來建構 API 端點，移除後可能導致排程功能無法正常運作。請確認 scheduling.init() 是否已改為從其他來源取得 apiUrl，或此參數已不再需要。

**判斷依據**：diff 中 `-        scheduling.init({` 和 `-            apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)` 被移除，改為 `+        scheduling.init(),`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8104 (cache hit 1536) ｜ completion tokens 589 ｜ PR #1</sub>