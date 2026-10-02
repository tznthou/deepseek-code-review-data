<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾器，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：將 token 儲存為整個物件、移除 noTimestamp 選項、改用 jwt.decode 驗證，可能導致 token 失效或安全性問題。建議先修正 JWT 相關變更再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存型別錯誤導致回傳值不一致 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 取代 jwt.verify 跳過簽章驗證 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能導致 JWT 簽章失敗 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/tests/api_top_locations.yaml:73` | 測試參數變更可能導致預期結果不正確 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存型別錯誤導致回傳值不一致</summary>

在 `getServerToken` 方法中，原本 `this._serverToken = tokenData.token` 儲存的是 token 字串，但現在改為 `this._serverToken = tokenData` 儲存整個物件。然而，回傳時仍使用 `token: this._serverToken`，這會導致回傳的 token 變成物件而非字串，造成呼叫端無法使用。

**失敗情境**：任何呼叫 `getServerToken` 的程式碼會收到 `{ token: { token: '...', exp: ... }, exp: ... }` 而非預期的 token 字串，可能導致認證失敗。

**建議**：改回 `this._serverToken = tokenData.token`，或調整回傳邏輯以正確提取 token 字串。

**判斷依據**：diff 中第 98 行將 `this._serverToken = tokenData.token` 改為 `this._serverToken = tokenData`，但回傳物件仍使用 `token: this._serverToken`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 取代 jwt.verify 跳過簽章驗證</summary>

在 `_isJWTExpired` 方法中，原本使用 `jwt.verify` 來驗證 token 的簽章和有效性，但現在改為 `jwt.decode`，這只解碼 payload 而不驗證簽章。這會導致攻擊者可以偽造 token 來繞過過期檢查，進而使用無效或惡意的 token。

**失敗情境**：攻擊者可以構造一個帶有任意 `exp` 的 JWT，即使簽章無效，`_isJWTExpired` 仍會回傳 false，使系統接受該 token。

**建議**：改回 `jwt.verify`，或使用其他方式驗證簽章。

**判斷依據**：diff 中第 164 行將 `jwt.verify` 改為 `jwt.decode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能導致 JWT 簽章失敗</summary>

原本 `jwt.sign` 使用 `{noTimestamp: true}` 來避免自動加入 `iat` 欄位，但現在移除了該選項。這會導致 JWT 中包含 `iat`（簽發時間），而 payload 中已有自訂的 `exp` 欄位。若 Tinybird 端預期 token 中沒有 `iat`，可能導致驗證失敗。

**失敗情境**：Tinybird 驗證 JWT 時若檢查 `iat` 欄位，可能因格式或存在性不符而拒絕 token。

**建議**：確認 Tinybird 端是否接受 `iat`，若否，請保留 `noTimestamp: true`。

**判斷依據**：diff 中第 147 行移除了 `{noTimestamp: true}` 選項。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/tests/api_top_locations.yaml:73</code> 測試參數變更可能導致預期結果不正確</summary>

在「Test with multiple filters combined」測試中，參數從 `device=desktop&browser=firefox` 改為 `source=bing.com&pathname=%2Fabout%2F`，但預期結果只包含兩筆資料。需要確認新的過濾條件是否正確對應到預期結果，否則測試可能無法通過或失去意義。

**失敗情境**：若 `source=bing.com` 和 `pathname=%2Fabout%2F` 的組合在測試資料中沒有對應的記錄，測試會失敗。

**建議**：驗證測試資料是否包含符合新條件的記錄，並確認預期結果正確。

**判斷依據**：diff 中該行參數被修改，但預期結果僅有兩筆，需確認資料一致性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15948 (cache hit 15872) ｜ completion tokens 1333 ｜ PR #12</sub>