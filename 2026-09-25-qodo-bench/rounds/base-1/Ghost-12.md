<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 的 JWT 處理變更：`_serverToken` 改存整個 token 物件，但 `_isJWTExpired` 改用 `jwt.decode` 且未驗證簽章，可能導致使用偽造 token 或快取行為異常。建議先修正 JWT 驗證邏輯再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | JWT 驗證改為 decode 導致簽章未驗證 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | _serverToken 型別變更可能導致後續使用錯誤 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | JWT 簽署移除 noTimestamp 可能影響 token 格式 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> JWT 驗證改為 decode 導致簽章未驗證</summary>

`_isJWTExpired` 從 `jwt.verify` 改為 `jwt.decode`，這會跳過簽章驗證。攻擊者可以偽造一個帶有未來 `exp` 的 token，通過過期檢查，進而使用無效的 token 存取 Tinybird API。建議改回 `jwt.verify`，或在 `_isJWTExpired` 中明確驗證簽章。

**判斷依據**：diff 中 `_isJWTExpired` 方法內 `jwt.verify` 被替換為 `jwt.decode`，且未見其他簽章驗證步驟。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> _serverToken 型別變更可能導致後續使用錯誤</summary>

`_serverToken` 原本存 token 字串，現在改存整個 token 物件（包含 `token` 和 `exp`）。若其他程式碼仍預期 `_serverToken` 是字串，可能導致型別錯誤或功能失效。請確認所有使用 `_serverToken` 的地方都已更新。

**判斷依據**：diff 中 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`，但未見其他使用處的修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> JWT 簽署移除 noTimestamp 可能影響 token 格式</summary>

`jwt.sign` 原本有 `{noTimestamp: true}`，現在移除後 token 會包含 `iat` 欄位。若 Tinybird 端對 token 格式有特定要求，可能導致驗證失敗。建議確認 Tinybird 是否接受帶有 `iat` 的 token。

**判斷依據**：diff 中 `jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為 `jwt.sign(payload, this.tinybirdConfig.adminToken);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13629 (cache hit 1536) ｜ completion tokens 802 ｜ PR #12</sub>