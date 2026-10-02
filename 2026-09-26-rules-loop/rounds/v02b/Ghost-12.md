<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中 device、browser、os 的過濾條件，並更新了對應的測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：_serverToken 改存整個 tokenData 物件，但 _isJWTExpired 改用 jwt.decode 且未驗證簽章，可能導致使用過期或偽造的 token。建議先修正 JWT 驗證邏輯再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | JWT 驗證被移除，可能接受過期或偽造的 token | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | _serverToken 型別不一致，可能導致後續使用錯誤 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | JWT 簽署時移除 noTimestamp 選項，可能導致 token 格式變更 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> JWT 驗證被移除，可能接受過期或偽造的 token</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 來驗證 token 的簽章與過期時間，現在改成 `jwt.decode`，這只會解碼 payload 而不會驗證簽章。這表示攻擊者可以偽造一個帶有任意 `exp` 的 token，或者使用已過期的 token，只要 payload 中的 `exp` 大於目前時間，就會被視為有效。這會導致未授權的 Tinybird 存取。

建議改回 `jwt.verify`，並在 catch 中處理驗證失敗的情況。

**判斷依據**：diff 中 `_isJWTExpired` 的實作從 `jwt.verify` 改為 `jwt.decode`，且沒有其他驗證步驟。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> _serverToken 型別不一致，可能導致後續使用錯誤</summary>

在 `getServerToken` 中，原本 `this._serverToken` 儲存的是 token 字串，現在改成儲存整個 `tokenData` 物件（包含 `token` 和 `exp`）。但在其他地方（例如 `_isJWTExpired` 的呼叫）可能仍然預期它是字串。這會導致型別錯誤或邏輯錯誤。

建議確認所有使用 `_serverToken` 的地方，並統一儲存型別。

**判斷依據**：diff 中 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`，但 `_isJWTExpired` 的參數型別未變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> JWT 簽署時移除 noTimestamp 選項，可能導致 token 格式變更</summary>

原本 `jwt.sign` 使用 `{noTimestamp: true}` 來避免自動加入 `iat`（issued at）欄位，現在移除了這個選項。這會讓 token 包含 `iat`，可能影響 Tinybird 端對 token 的驗證（如果它預期沒有 `iat`）。此外，`_isJWTExpired` 現在依賴 `exp` 欄位，但 `exp` 是手動加入的，移除 `noTimestamp` 後可能與自動產生的 `iat` 產生混淆。

建議確認 Tinybird 是否接受帶有 `iat` 的 token，或保留 `noTimestamp`。

**判斷依據**：diff 中 `jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為 `jwt.sign(payload, this.tinybirdConfig.adminToken);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15938 (cache hit 15872) ｜ completion tokens 961 ｜ PR #12</sub>