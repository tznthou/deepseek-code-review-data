<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：_serverToken 改存整個 tokenData 物件、_generateToken 移除 noTimestamp 選項、_isJWTExpired 改用 jwt.decode 而非 jwt.verify。這些變更可能導致 token 驗證失效或安全性問題，需要進一步確認。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存型別錯誤導致後續使用失敗 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能導致 JWT 簽章驗證失敗 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 取代 jwt.verify 導致 token 驗證失效 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存型別錯誤導致後續使用失敗</summary>

`_serverToken` 原本儲存 token 字串，現在改存整個 `tokenData` 物件。但在 `getServerToken` 方法中，回傳值仍使用 `this._serverToken`，這會導致回傳物件而非字串，可能造成呼叫端錯誤。

建議：保留 `this._serverToken = tokenData.token`，或調整回傳邏輯。

**判斷依據**：diff 中將 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`，但後續 `return { token: this._serverToken, ... }` 未變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能導致 JWT 簽章驗證失敗</summary>

`jwt.sign` 原本使用 `{noTimestamp: true}`，現在移除該選項。這會讓 JWT 包含 `iat` claim，可能影響 Tinybird 端對 token 的驗證（若 Tinybird 預期無 `iat`）。

建議：確認 Tinybird 是否接受含 `iat` 的 token，若否則保留 `noTimestamp: true`。

**判斷依據**：diff 中移除了 `{noTimestamp: true}` 選項。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 取代 jwt.verify 導致 token 驗證失效</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 驗證簽章，現在改用 `jwt.decode` 僅解碼不驗證。這會讓過期或偽造的 token 被視為有效，造成安全漏洞。

建議：改回 `jwt.verify`，或若僅需檢查過期時間，應在解碼後額外驗證簽章。

**判斷依據**：diff 中將 `jwt.verify` 改為 `jwt.decode`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15928 (cache hit 15872) ｜ completion tokens 797 ｜ PR #12</sub>