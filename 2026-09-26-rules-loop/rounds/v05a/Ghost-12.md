<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：`_serverToken` 改存整個 token 物件，但 `_isJWTExpired` 改用 `jwt.decode` 且未驗證簽章，可能導致接受過期或偽造的 token。此外，`_generateToken` 移除了 `noTimestamp` 選項，可能影響 token 格式。整體而言，移除過濾條件的部分風險較低，但 JWT 變更需要仔細審查。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | JWT 驗證改為 decode 導致安全性漏洞 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT 過期檢查可能誤判 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 可能影響 token 格式 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | JWT 解碼未處理錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> JWT 驗證改為 decode 導致安全性漏洞</summary>

`_isJWTExpired` 從 `jwt.verify` 改為 `jwt.decode`，這不會驗證簽章。攻擊者可以偽造一個帶有任意 `exp` 的 token，只要格式正確就會被接受，進而取得未授權的 Tinybird 存取權。應改回 `jwt.verify` 並處理可能的驗證錯誤。

**判斷依據**：diff 中 `_isJWTExpired` 方法內將 `jwt.verify` 改為 `jwt.decode`，且未進行簽章驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT 過期檢查可能誤判</summary>

`_isJWTExpired` 使用 `jwt.decode` 取得 `exp`，但 `_generateToken` 現在使用 `jwt.sign` 時未指定 `noTimestamp`，因此 token 會包含 `iat` 和 `exp`。然而，`_serverToken` 現在儲存整個 token 物件，但 `_isJWTExpired` 仍預期收到 token 字串。呼叫處 `this._isJWTExpired(this._serverToken)` 傳入的是物件，可能導致 `jwt.decode` 收到非字串而拋出錯誤或回傳 null，造成過期判斷失效。應統一 token 的儲存與傳遞型別。

**判斷依據**：diff 中 `_serverToken` 被指派為 `tokenData`（物件），但 `_isJWTExpired` 的參數型別未更新，且呼叫處仍傳入 `this._serverToken`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 可能影響 token 格式</summary>

`_generateToken` 原本使用 `jwt.sign(payload, adminToken, {noTimestamp: true})`，現在改為 `jwt.sign(payload, adminToken)`，這會自動加入 `iat` 和 `exp`。若 Tinybird 端預期 token 不含時間戳，可能導致驗證失敗。需確認 Tinybird 對 token 的要求。

**判斷依據**：diff 中移除了 `{noTimestamp: true}` 選項。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> JWT 解碼未處理錯誤</summary>

`jwt.decode` 可能因 token 格式錯誤而拋出例外，但此處未使用 try-catch 包裹。若 token 損壞，可能導致未處理的例外。建議加入錯誤處理。

**判斷依據**：diff 中 `_isJWTExpired` 方法內直接呼叫 `jwt.decode`，未見錯誤處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15862 (cache hit 13568) ｜ completion tokens 1061 ｜ PR #12</sub>