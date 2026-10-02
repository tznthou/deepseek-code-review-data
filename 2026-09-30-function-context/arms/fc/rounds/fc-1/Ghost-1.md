<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 XML-RPC ping 服務（xmlrpc.js 及其測試），並在 boot.js 中移除了相關初始化。主要風險在於 boot.js 中 `scheduling.init()` 的呼叫方式被簡化，移除了原本傳入的 `apiUrl` 參數，可能導致排程服務無法正確建構 API URL。此外，`emailAddressService.init()` 的呼叫從同步改為非同步，需確認其餘服務是否依賴其完成。整體而言，移除 XML-RPC 服務本身風險較低，但需確保相關設定與相依性已完全清理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/boot.js:368` | scheduling.init() 缺少 apiUrl 參數可能導致排程服務無法正常運作 | 0.80 |
| 🔸 | Minor | `ghost/core/core/boot.js:352` | emailAddressService.init() 改為非同步呼叫可能影響相依服務 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/boot.js:368</code> scheduling.init() 缺少 apiUrl 參數可能導致排程服務無法正常運作</summary>

原本 `scheduling.init()` 會傳入 `apiUrl` 參數，用於建構排程服務所需的 API URL。移除後，排程服務可能無法正確取得 API 位址，導致排程任務失敗或無法觸發。建議確認 `scheduling.init()` 是否已改為從其他來源取得 API URL，或此參數是否已不再需要。

**判斷依據**：diff 中原本的 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 被改為 `scheduling.init()`，且 `urlUtils` 仍被保留但未使用於此處。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/boot.js:352</code> emailAddressService.init() 改為非同步呼叫可能影響相依服務</summary>

原本 `emailAddressService.init()` 是同步呼叫（前面有 `await`），現在改為在 `Promise.all` 中非同步執行。若其他服務（如 newsletter 或 email service）依賴 email address service 初始化完成，可能導致競態條件。建議確認這些服務是否已正確處理非同步初始化。

**判斷依據**：diff 中原本的 `await emailAddressService.init(),` 被移除，並在 `Promise.all` 陣列中加入 `emailAddressService.init(),`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6292 (cache hit 1536) ｜ completion tokens 592 ｜ PR #1</sub>