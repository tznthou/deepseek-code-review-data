<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新相關測試。主要風險在於 TinybirdService.js 的 JWT 處理變更：_serverToken 改存整個 tokenData 物件，但後續程式碼仍以字串方式使用，可能導致驗證失敗；同時 _isJWTExpired 改用 jwt.decode 跳過簽章驗證，若 token 被竄改可能造成安全問題。建議先修正 JWT 相關變更再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | _serverToken 型別不一致可能導致 JWT 驗證失敗 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 跳過簽章驗證可能接受被竄改的 token | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能導致 token 包含 iat 欄位 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> _serverToken 型別不一致可能導致 JWT 驗證失敗</summary>

在 `getServerToken` 中，原本 `this._serverToken = tokenData.token` 儲存的是字串，但現在改為 `this._serverToken = tokenData` 儲存整個物件。然而，後續使用 `this._serverToken` 的地方（例如 `_isJWTExpired(this._serverToken)` 或回傳給呼叫端）仍預期它是字串。這會導致 `jwt.decode` 收到物件而非字串，可能拋出錯誤或回傳 null，進而使 token 永遠被視為過期，每次請求都重新產生 token，造成效能問題或功能失效。

建議：維持 `this._serverToken = tokenData.token`，或同步修改所有使用 `_serverToken` 的地方以處理物件型別。

**判斷依據**：diff 中 `-                this._serverToken = tokenData.token;` 改為 `+                this._serverToken = tokenData;`，但同檔案其他部分（如 `_isJWTExpired` 呼叫）未見對應調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 跳過簽章驗證可能接受被竄改的 token</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 來驗證 token 的簽章與有效性，現在改為 `jwt.decode` 僅解碼 payload 而不驗證簽章。這表示攻擊者若取得或猜測到 token，可以竄改 payload（例如延長 `exp`）而不被偵測，導致過期 token 被接受。雖然此 token 可能僅用於內部服務，但仍存在安全風險。

建議：若需驗證過期，應使用 `jwt.verify` 並捕捉 `TokenExpiredError` 來判斷是否過期，或至少使用 `jwt.verify` 的 `ignoreExpiration` 選項。

**判斷依據**：diff 中 `-            const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 改為 `+            const decoded = jwt.decode(token);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能導致 token 包含 iat 欄位</summary>

原本 `jwt.sign` 使用 `{noTimestamp: true}` 來避免在 payload 中加入 `iat`（issued at）欄位，現在移除了該選項，因此產生的 token 會包含 `iat`。這可能影響 token 的驗證邏輯或與其他系統的相容性，但通常不會造成直接問題。若無特定理由，建議保留 `noTimestamp: true` 以維持原有行為。

**判斷依據**：diff 中 `-        const token = jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為 `+        const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13629 (cache hit 13568) ｜ completion tokens 1034 ｜ PR #12</sub>