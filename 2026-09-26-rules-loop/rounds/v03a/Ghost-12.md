<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：將 token 儲存為完整物件可能導致後續使用錯誤，且將 jwt.verify 改為 jwt.decode 會跳過簽章驗證，可能造成安全性問題。建議先修正 JWT 相關變更再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存為完整物件，導致後續使用錯誤 | 0.95 |
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | JWT 驗證改為解碼，跳過簽章驗證 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | JWT 簽署移除 noTimestamp 選項，可能導致 token 包含 iat 而影響過期判斷 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | token 儲存型別不一致可能導致快取失效 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存為完整物件，導致後續使用錯誤</summary>

在 `getServerToken` 方法中，原本將 `tokenData.token` 存入 `this._serverToken`，但現在改為存入整個 `tokenData` 物件。然而，回傳時仍使用 `this._serverToken`，這會導致回傳的 token 變成物件而非字串，造成呼叫端錯誤。

建議改回 `this._serverToken = tokenData.token;`。

**判斷依據**：diff 中將 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`，但回傳處仍為 `return { token: this._serverToken, ... }`，型別不符。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> JWT 驗證改為解碼，跳過簽章驗證</summary>

在 `_isJWTExpired` 方法中，將 `jwt.verify` 改為 `jwt.decode`。`jwt.decode` 僅解碼 payload，不驗證簽章，攻擊者可偽造 token 並設定任意 `exp` 來繞過過期檢查。

建議改回 `jwt.verify`，並處理可能的驗證錯誤。

**判斷依據**：diff 中將 `jwt.verify(token, this.tinybirdConfig.adminToken)` 改為 `jwt.decode(token)`，失去簽章驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> JWT 簽署移除 noTimestamp 選項，可能導致 token 包含 iat 而影響過期判斷</summary>

原本 `jwt.sign` 使用 `{noTimestamp: true}` 來避免自動加入 `iat`，現在移除該選項後，token 會包含 `iat`。雖然 `_isJWTExpired` 目前使用 `jwt.decode` 讀取 `exp`，但若未來改回 `jwt.verify`，`iat` 的存在可能影響某些驗證邏輯。建議確認此變更的必要性，或保留 `noTimestamp: true`。

**判斷依據**：diff 中移除了 `{noTimestamp: true}` 選項。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> token 儲存型別不一致可能導致快取失效</summary>

若 `this._serverToken` 被存為物件，則後續比較或使用時可能因型別不符而無法正確判斷快取有效性。建議統一儲存 token 字串。

**判斷依據**：與前一個 finding 相關，但著重於快取邏輯的影響。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15948 (cache hit 13568) ｜ completion tokens 998 ｜ PR #12</sub>