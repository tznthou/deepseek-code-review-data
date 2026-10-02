<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 管線中 device、browser、os 的過濾條件，並同步刪除相關測試案例，同時調整了 JWT 產生與驗證邏輯。主要風險在於 JWT 驗證從 verify 改為 decode，可能導致接受過期或無效的 token，造成安全漏洞。此外，移除過濾條件可能影響前端功能，需確認前端已不再使用這些參數。建議優先修正 JWT 驗證邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | JWT 驗證改用 decode 導致接受過期或無效 token | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存方式變更可能導致型別不一致 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能改變 token 內容 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> JWT 驗證改用 decode 導致接受過期或無效 token</summary>

在 `_isJWTExpired` 方法中，原本使用 `jwt.verify` 來驗證 token 的簽名與有效性，現在改為 `jwt.decode`，這只會解碼 payload 而不驗證簽名。這表示攻擊者可以偽造任意 token（只要 payload 中包含 `exp` 欄位），系統就會接受，可能導致未授權存取 Tinybird 資料。

**失敗情境**：攻擊者自行產生一個帶有未來 `exp` 的 JWT（無需知道 adminToken），即可通過此檢查，取得有效的 Tinybird 存取權。

**建議**：恢復使用 `jwt.verify`，並保留原本的 `noTimestamp` 選項（如果原本有設定）。

**判斷依據**：diff 中 `-            const decoded = jwt.verify(token, this.tinybirdConfig.adminToken);` 被改為 `+            const decoded = jwt.decode(token);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存方式變更可能導致型別不一致</summary>

在 `getOrCreateServerToken` 中，原本 `this._serverToken = tokenData.token`（字串），現在改為 `this._serverToken = tokenData`（物件）。這可能影響其他使用 `_serverToken` 的地方，若後續程式碼預期它是字串，會造成錯誤。

**失敗情境**：若有其他方法直接使用 `this._serverToken` 作為 Authorization header 的值，會變成 `[object Object]`，導致 API 呼叫失敗。

**建議**：確認所有使用 `_serverToken` 的地方，並保持型別一致。若需要同時儲存 token 和 exp，可考慮分開儲存或調整相關程式碼。

**判斷依據**：diff 中 `-                this._serverToken = tokenData.token;` 改為 `+                this._serverToken = tokenData;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能改變 token 內容</summary>

在 `_generateToken` 中，原本 `jwt.sign` 有 `{noTimestamp: true}` 選項，現在移除了。這會讓 JWT 自動加入 `iat`（issued at）欄位，可能影響 token 的 payload 結構，若 Tinybird 端有驗證 payload 的特定格式，可能導致問題。

**失敗情境**：若 Tinybird 端預期 token 中沒有 `iat`，加入後可能導致驗證失敗。

**建議**：確認 Tinybird 端是否接受帶有 `iat` 的 token，若無必要，保留 `noTimestamp: true`。

**判斷依據**：diff 中 `-        const token = jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true});` 改為 `+        const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15938 (cache hit 1536) ｜ completion tokens 1033 ｜ PR #12</sub>