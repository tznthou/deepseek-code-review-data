<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。同時調整了 TinybirdService 的 JWT 處理：將 token 儲存為完整物件、移除 noTimestamp 選項、改用 jwt.decode 進行過期檢查。主要風險在於 JWT 變更可能影響 token 有效性與過期判斷邏輯，需確認與 Tinybird 的相容性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存方式變更可能導致回傳格式不一致 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 可能導致 Tinybird 拒絕 token | 0.75 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 改用 jwt.decode 可能無法正確驗證 token 有效性 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存方式變更可能導致回傳格式不一致</summary>

原本 `this._serverToken` 儲存的是 token 字串，現在改為儲存整個 tokenData 物件。這會影響 `getServerToken` 的回傳值：原本回傳 `{token: this._serverToken, exp: this._serverTokenExp}`，現在 `this._serverToken` 是物件，會變成巢狀結構。請確認所有呼叫端是否預期 token 為字串。

**判斷依據**：diff 中 `-                this._serverToken = tokenData.token;` 改為 `+                this._serverToken = tokenData;`，且下方回傳仍為 `return { token: this._serverToken, exp: this._serverTokenExp };`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 可能導致 Tinybird 拒絕 token</summary>

原本 `jwt.sign` 使用 `{noTimestamp: true}`，現在移除該選項，token 將包含 `iat` claim。若 Tinybird 端驗證時不預期有 `iat`，可能導致 token 無效。請確認 Tinybird 是否接受含 `iat` 的 JWT。

**判斷依據**：diff 中 `-        const token = jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為 `+        const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 改用 jwt.decode 可能無法正確驗證 token 有效性</summary>

原本使用 `jwt.verify` 來檢查 token 是否過期，現在改用 `jwt.decode`。`jwt.decode` 不會驗證簽名，且若 token 格式錯誤可能回傳 null，但程式碼未處理 null 情況。此外，若 token 被竄改，`jwt.decode` 仍會回傳 payload，可能導致過期判斷錯誤。建議保留 `jwt.verify` 或加入簽名驗證。

**判斷依據**：diff 中 `-            const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 改為 `+            const decoded = jwt.decode(token);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13593 (cache hit 13568) ｜ completion tokens 840 ｜ PR #12</sub>