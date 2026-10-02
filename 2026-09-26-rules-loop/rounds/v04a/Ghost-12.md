<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：_serverToken 改存整個 token 物件、jwt.sign 移除了 noTimestamp 選項、_isJWTExpired 改用 jwt.decode。這些變更可能導致 token 驗證邏輯失效或安全性問題，需要進一步確認。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存型別不一致可能導致驗證失敗 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 可能導致 JWT 簽章驗證失敗 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 取代 jwt.verify 可能接受無效 token | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存型別不一致可能導致驗證失敗</summary>

`_serverToken` 原本儲存 token 字串，現在改存整個 token 物件（`this._serverToken = tokenData;`），但 `_isJWTExpired` 仍以字串參數呼叫 `jwt.decode(token)`。若 `tokenData` 是物件，`jwt.decode` 會收到非字串而拋出錯誤或回傳 null，導致 token 永遠被視為過期，每次請求都重新產生 token。

建議：確認 `_generateToken` 回傳的 `token` 欄位是字串，並將 `_serverToken` 設為 `tokenData.token`，或調整 `_isJWTExpired` 以接受物件。

**判斷依據**：diff 中 `-                this._serverToken = tokenData.token;` 改為 `+                this._serverToken = tokenData;`，而 `_isJWTExpired` 仍呼叫 `jwt.decode(token)`，型別不符。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 可能導致 JWT 簽章驗證失敗</summary>

`jwt.sign` 原本使用 `{noTimestamp: true}` 來避免加入 `iat` claim，現在移除了該選項，導致 token 包含 `iat`。若 Tinybird 端驗證 token 時預期沒有 `iat`，可能導致驗證失敗。

建議：確認 Tinybird 對 token 的驗證邏輯，若需要無 `iat` 則保留 `noTimestamp: true`。

**判斷依據**：diff 中 `-        const token = jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為 `+        const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 取代 jwt.verify 可能接受無效 token</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 驗證簽章，現在改用 `jwt.decode` 僅解碼不驗證。這可能導致攻擊者偽造 token 或使用過期 token 通過檢查，造成安全風險。

建議：保留 `jwt.verify` 以確保 token 完整性，或明確說明為何不需要驗證簽章。

**判斷依據**：diff 中 `-            const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 改為 `+            const decoded = jwt.decode(token);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14818 (cache hit 13568) ｜ completion tokens 928 ｜ PR #12</sub>