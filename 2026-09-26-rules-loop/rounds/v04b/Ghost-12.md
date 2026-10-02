<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：_serverToken 改存整個 tokenData 物件、_generateToken 移除 noTimestamp 選項、_isJWTExpired 改用 jwt.decode 而非 jwt.verify，這些變更可能導致 token 驗證失效或安全性問題。建議先確認 JWT 變更的必要性與正確性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存型別變更導致後續使用錯誤 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能導致 JWT 驗證失敗 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 取代 jwt.verify 可能導致安全性問題 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存型別變更導致後續使用錯誤</summary>

原本 `this._serverToken` 儲存的是 token 字串，現在改存整個 tokenData 物件。但在 `getServerToken` 方法中，回傳時仍使用 `this._serverToken`，這會導致回傳物件而非字串，造成呼叫端錯誤。建議改回儲存 token 字串，或調整回傳邏輯。

**判斷依據**：diff 中 `-                this._serverToken = tokenData.token;` 改為 `+                this._serverToken = tokenData;`，但後續回傳仍使用 `this._serverToken`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能導致 JWT 驗證失敗</summary>

原本 `jwt.sign` 使用 `{noTimestamp: true}`，現在移除該選項。若 Tinybird 端預期 token 不含 `iat` claim，可能導致驗證失敗。需確認 Tinybird 對 token 的要求。

**判斷依據**：diff 中 `-        const token = jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為 `+        const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 取代 jwt.verify 可能導致安全性問題</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 驗證 token 簽名，現在改用 `jwt.decode` 僅解碼不驗證。這可能讓攻擊者偽造 token 並繞過過期檢查。建議保留 `jwt.verify` 以確保 token 完整性。

**判斷依據**：diff 中 `-            const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 改為 `+            const decoded = jwt.decode(token);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14818 (cache hit 14720) ｜ completion tokens 791 ｜ PR #12</sub>