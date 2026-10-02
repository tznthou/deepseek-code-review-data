<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 的 JWT 處理變更：_serverToken 改存整個 tokenData 物件、_generateToken 移除 noTimestamp 選項、_isJWTExpired 改用 jwt.decode 而非 jwt.verify。這些變更可能導致 token 驗證失效或安全性問題，需要進一步確認。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | _serverToken 儲存整個 tokenData 物件，可能導致後續使用錯誤 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能導致 JWT 產生時間戳，影響過期判斷 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 而非 jwt.verify 可能導致安全性問題 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> _serverToken 儲存整個 tokenData 物件，可能導致後續使用錯誤</summary>

在 `getServerToken` 方法中，原本 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`。這會讓 `_serverToken` 變成一個物件而非 token 字串。後續程式碼若直接使用 `this._serverToken` 作為 token 字串（例如在 HTTP header 中），將導致驗證失敗。請確認所有使用 `_serverToken` 的地方，並修正為儲存 `tokenData.token`。

**判斷依據**：diff 中第 98 行：`-                this._serverToken = tokenData.token;` 改為 `+                this._serverToken = tokenData;`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能導致 JWT 產生時間戳，影響過期判斷</summary>

在 `_generateToken` 中，`jwt.sign` 原本有 `{noTimestamp: true}` 選項，現在被移除。這會讓 JWT 包含 `iat`（issued at）欄位。如果 Tinybird 端驗證時預期沒有 `iat`，可能導致 token 被拒絕。另外，`_isJWTExpired` 改用 `jwt.decode` 後，若 token 沒有 `exp` 欄位（因為 `noTimestamp` 移除後可能仍無 `exp`？），會回傳 true，造成 token 永遠被視為過期。請確認 Tinybird 對 JWT 的要求，並確保 `exp` 欄位正確設定。

**判斷依據**：diff 中第 147 行：`-        const token = jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為 `+        const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 而非 jwt.verify 可能導致安全性問題</summary>

在 `_isJWTExpired` 中，原本使用 `jwt.verify` 驗證 token 的簽名和有效性，現在改為 `jwt.decode`。`jwt.decode` 只解碼 payload，不驗證簽名，因此攻擊者可以偽造 token 並通過過期檢查。這可能導致未授權的存取。請改回使用 `jwt.verify`，並處理可能的驗證錯誤。

**判斷依據**：diff 中第 164 行：`-            const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 改為 `+            const decoded = jwt.decode(token);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13629 (cache hit 13568) ｜ completion tokens 950 ｜ PR #12</sub>