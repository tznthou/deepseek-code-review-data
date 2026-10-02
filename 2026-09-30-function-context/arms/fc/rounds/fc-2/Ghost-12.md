<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新相關測試。主要風險在於 TinybirdService.js 的 JWT 處理變更：將 token 儲存為物件可能導致下游使用錯誤，且改用 jwt.decode 跳過簽章驗證，可能接受偽造 token。建議先修正這兩個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存型別變更可能導致下游使用錯誤 | 0.95 |
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 跳過簽章驗證，可能接受偽造 token | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | jwt.decode 可能回傳 null 或 string，未處理型別 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存型別變更可能導致下游使用錯誤</summary>

原本 `this._serverToken` 儲存的是 token 字串，現在改存 `tokenData` 物件。但 `getToken` 回傳時仍將 `this._serverToken` 直接放入 `token` 欄位，導致呼叫端拿到的是物件而非字串。若呼叫端預期 `token` 為字串（例如用於 Authorization header），將造成驗證失敗或型別錯誤。

建議：保留 `this._serverToken` 為字串，或明確回傳 `tokenData.token`。

**判斷依據**：diff 中 `-                this._serverToken = tokenData.token;` 改為 `+                this._serverToken = tokenData;`，但下方 `return { token: this._serverToken, exp: this._serverTokenExp };` 未同步調整。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 跳過簽章驗證，可能接受偽造 token</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 驗證簽章，現在改用 `jwt.decode` 僅解碼 payload。攻擊者可偽造任意 exp 的 token，繞過過期檢查，導致服務使用無效或惡意 token 進行後續請求。

建議：改回 `jwt.verify`，或若需避免驗證開銷，應在後續使用 token 時進行完整驗證。

**判斷依據**：diff 中 `-            const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 改為 `+            const decoded = jwt.decode(token);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> jwt.decode 可能回傳 null 或 string，未處理型別</summary>

`jwt.decode` 在 token 無效時可能回傳 `null` 或 `string`（若 payload 非物件）。目前程式碼僅檢查 `typeof decoded !== 'object'`，但未檢查 `decoded === null`，若為 null 則 `decoded.exp` 會拋出 TypeError，導致 catch 區塊回傳 true（視為過期），可能造成不必要的 token 重新產生。

建議：先檢查 `decoded` 是否為 null，或使用 `jwt.verify` 並處理其拋出的錯誤。

**判斷依據**：diff 中新增的 `jwt.decode` 呼叫，其回傳值未做 null 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14283 (cache hit 14208) ｜ completion tokens 886 ｜ PR #12</sub>