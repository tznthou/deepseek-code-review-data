<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：將 token 儲存為完整物件、改用 jwt.decode 驗證過期，可能導致型別不一致與安全性疑慮。建議先修正 JWT 相關變更，再合併其餘部分。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存型別不一致 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 取代 jwt.verify 可能導致安全性問題 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能影響 token 格式 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存型別不一致</summary>

在 `getServerToken` 方法中，原本 `this._serverToken` 儲存的是字串（`tokenData.token`），現在改為儲存整個 `tokenData` 物件。但 `_isJWTExpired` 方法仍預期收到字串 token，且其他程式碼可能直接使用 `this._serverToken` 作為 token 字串。這會導致型別錯誤或驗證失敗。

建議：保留 `this._serverToken = tokenData.token;`，或同步修改所有使用 `_serverToken` 的地方。

**判斷依據**：diff 中將 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`，但 `_isJWTExpired` 仍以字串參數呼叫 `jwt.decode`，且回傳的 token 可能被其他服務直接使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 取代 jwt.verify 可能導致安全性問題</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 來驗證 token 的簽名與過期時間，現在改為 `jwt.decode` 僅解碼而不驗證簽名。這可能讓攻擊者偽造 token 或繞過過期檢查。

建議：若僅需檢查過期時間，可先解碼取得 exp，但仍應在必要時驗證簽名；或保留 `jwt.verify` 並處理其拋出的錯誤。

**判斷依據**：diff 中將 `jwt.verify(token, this.tinybirdConfig.adminToken)` 改為 `jwt.decode(token)`，移除了簽名驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能影響 token 格式</summary>

原本 `jwt.sign` 使用 `{noTimestamp: true}` 來避免自動加入 `iat` 欄位，現在移除了該選項。這會導致 token 中包含 `iat`，可能影響與 Tinybird 的相容性或 token 大小。

建議：確認 Tinybird 是否接受含 `iat` 的 token，若無必要可保留原選項。

**判斷依據**：diff 中移除了 `{noTimestamp: true}` 選項。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15938 (cache hit 13568) ｜ completion tokens 859 ｜ PR #12</sub>