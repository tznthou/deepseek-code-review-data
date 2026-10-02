<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試與 JWT 處理邏輯。主要風險在於 `TinybirdService.js` 中 `_serverToken` 的型態從字串改為物件，但 `getToken` 回傳的 `token` 欄位仍標示為字串，可能導致下游使用錯誤；此外 `_isJWTExpired` 改用 `jwt.decode` 不再驗證簽章，若 token 被竄改可能造成安全問題。建議優先修正這兩個問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | `_serverToken` 型態不一致可能導致下游錯誤 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 改用 `jwt.decode` 跳過簽章驗證，可能接受被竄改的 token | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> `_serverToken` 型態不一致可能導致下游錯誤</summary>

`_serverToken` 原本存的是字串（`tokenData.token`），現在改存整個 `tokenData` 物件。但 `getToken` 回傳的 `token` 欄位型態仍標示為 `string`，且其他使用 `getToken` 的程式碼可能預期收到字串。若下游直接將 `token` 用於 HTTP header 或字串操作，會得到 `[object Object]` 或錯誤。建議確認所有呼叫端，或改回存字串並另外保存 exp。

**判斷依據**：diff 中 `-                this._serverToken = tokenData.token;` 改為 `+                this._serverToken = tokenData;`，但 `getToken` 的回傳型態註解未更新。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 改用 `jwt.decode` 跳過簽章驗證，可能接受被竄改的 token</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 驗證簽章，現在改用 `jwt.decode` 只解碼不驗證。若攻擊者能取得或猜測 token 結構，可能偽造未過期的 token 來繞過過期檢查。雖然後續使用 token 時 Tinybird 仍會驗證簽章，但此處的過期判斷可能被欺騙，導致服務使用已過期或無效的 token 進行請求。建議改回 `jwt.verify` 或明確說明為何不需要驗證。

**判斷依據**：diff 中 `-            const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 改為 `+            const decoded = jwt.decode(token);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14283 (cache hit 4992) ｜ completion tokens 700 ｜ PR #12</sub>