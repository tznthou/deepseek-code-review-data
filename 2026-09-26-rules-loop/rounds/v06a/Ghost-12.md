<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：將 token 儲存為完整物件、移除 noTimestamp 選項、改用 jwt.decode 驗證，可能導致 token 失效或安全性問題。建議先修正 JWT 相關變更再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存型別錯誤導致後續使用失敗 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 可能導致 JWT 簽名失敗或驗證問題 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 取代 jwt.verify 可能接受無效 token | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT 過期檢查可能因型別錯誤而失效 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存型別錯誤導致後續使用失敗</summary>

`_serverToken` 原本儲存 token 字串，現在改為儲存整個 tokenData 物件。但在 `getServerToken` 回傳時仍使用 `this._serverToken`，這會導致回傳物件而非字串，造成呼叫端錯誤。

建議：保留 `this._serverToken = tokenData.token;` 或調整回傳邏輯。

**判斷依據**：diff 中將 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`，但後續 `return { token: this._serverToken, ... }` 未變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 可能導致 JWT 簽名失敗或驗證問題</summary>

原本 `jwt.sign` 使用 `{noTimestamp: true}`，移除後會自動加入 `iat` 欄位。若 Tinybird 端預期 token 不含 `iat`，可能導致驗證失敗。

建議：確認 Tinybird 對 token 的要求，若需無時間戳則保留該選項。

**判斷依據**：diff 中移除了 `{noTimestamp: true}` 選項。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 取代 jwt.verify 可能接受無效 token</summary>

`jwt.decode` 僅解碼 token，不驗證簽名。若 token 被竄改或簽名無效，仍可能通過檢查，導致安全風險。

建議：改回 `jwt.verify` 以確保 token 完整性。

**判斷依據**：diff 中將 `jwt.verify` 改為 `jwt.decode`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT 過期檢查可能因型別錯誤而失效</summary>

`_isJWTExpired` 接收 `this._serverToken`，但現在該值為物件而非字串，可能導致 `jwt.decode` 拋出錯誤或無法正確解碼。

建議：修正 token 儲存型別後，此問題應一併解決。

**判斷依據**：與第一個 finding 相關，token 型別錯誤會影響過期檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15928 (cache hit 13568) ｜ completion tokens 917 ｜ PR #12</sub>