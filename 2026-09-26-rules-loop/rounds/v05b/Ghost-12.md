<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：將 token 物件存入 _serverToken 可能導致後續使用時型別不一致；_generateToken 移除 noTimestamp 選項可能改變 token 內容；_isJWTExpired 改用 jwt.decode 不再驗證簽章，可能接受偽造 token。這些變更需要進一步確認其正確性與安全性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 物件被存入 _serverToken，可能導致後續使用型別錯誤 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 取代 jwt.verify 可能接受未簽名或偽造的 token | 0.85 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能改變 JWT 內容 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 物件被存入 _serverToken，可能導致後續使用型別錯誤</summary>

在 `getServerToken` 方法中，原本 `this._serverToken = tokenData.token;` 被改為 `this._serverToken = tokenData;`，這使得 `_serverToken` 現在儲存的是整個 token 物件（包含 `token` 和 `exp` 屬性），而不是 token 字串。後續程式碼若將 `_serverToken` 當作字串使用（例如在 HTTP header 中），可能會產生錯誤。建議改回儲存 `tokenData.token`，或確認所有使用 `_serverToken` 的地方都能正確處理物件。

**判斷依據**：diff 中此行由 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 取代 jwt.verify 可能接受未簽名或偽造的 token</summary>

在 `_isJWTExpired` 方法中，原本使用 `jwt.verify` 來驗證 token 的簽章並解碼，現在改為 `jwt.decode`，這只解碼而不驗證簽章。這意味著攻擊者可以偽造一個具有未來 `exp` 的 token，並被系統接受為有效。建議改回 `jwt.verify`，或明確說明為何此處不需要驗證簽章（例如 token 僅用於內部且來源可信）。

**判斷依據**：diff 中此行由 `const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 改為 `const decoded = jwt.decode(token);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能改變 JWT 內容</summary>

在 `_generateToken` 方法中，`jwt.sign` 的選項從 `{noTimestamp: true}` 改為無選項，這會導致 JWT 中包含標準的 `iat`（issued at）時間戳。如果 Tinybird 端依賴於無 `iat` 的 token，或者 token 的驗證邏輯對 `iat` 有特殊處理，這可能導致驗證失敗。建議確認 Tinybird 對 token 的要求，或保留 `noTimestamp: true`。

**判斷依據**：diff 中此行由 `const token = jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為無選項

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15862 (cache hit 15744) ｜ completion tokens 912 ｜ PR #12</sub>