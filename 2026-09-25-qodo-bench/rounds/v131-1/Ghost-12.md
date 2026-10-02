<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。同時調整了 JWT 的產生與驗證方式，但 `_serverToken` 的型態從字串改為物件，可能導致後續使用時發生型別錯誤。整體風險集中在 JWT 相關變更，建議先修正此問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | `_serverToken` 型態從字串改為物件，可能導致後續使用錯誤 | 0.95 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | JWT 驗證改為僅解碼，未驗證簽章 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | JWT 簽署時移除 `noTimestamp` 選項，可能影響 token 格式 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> `_serverToken` 型態從字串改為物件，可能導致後續使用錯誤</summary>

在 `getServerToken` 方法中，原本 `this._serverToken = tokenData.token;` 將 token 字串存入 `_serverToken`，但現在改為 `this._serverToken = tokenData;`，存入的是整個物件。然而，`_isJWTExpired` 方法仍預期接收 token 字串（呼叫 `jwt.decode(token)`），且其他可能使用 `_serverToken` 的地方（如回傳給呼叫端）也可能預期是字串。這會導致型別不一致，可能造成執行時期錯誤或驗證失敗。

**失敗情境**：當 `_serverToken` 被當作字串使用時（例如傳給 `jwt.decode` 或直接回傳），會因為它是物件而拋出錯誤或產生非預期行為。

**建議**：維持 `_serverToken` 為 token 字串，另外儲存 exp 或其他必要資訊。例如：
```js
this._serverToken = tokenData.token;
this._serverTokenExp = tokenData.exp;
```

**判斷依據**：diff 中將 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`，但 `_isJWTExpired` 仍呼叫 `jwt.decode(token)`，且其他程式碼可能依賴 `_serverToken` 為字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> JWT 驗證改為僅解碼，未驗證簽章</summary>

`_isJWTExpired` 方法原本使用 `jwt.verify(token, this.tinybirdConfig.adminToken)` 來驗證 token 的簽章與有效性，現在改為 `jwt.decode(token)`，只解碼而不驗證簽章。這會讓攻擊者可以偽造 token（只要 payload 包含有效的 `exp` 欄位），繞過驗證。

**失敗情境**：攻擊者自行產生一個帶有未來 `exp` 的 JWT，即使簽章無效，系統仍會視為有效，進而取得未授權的存取。

**建議**：保留 `jwt.verify` 來驗證簽章，若需要解碼 payload 可另行處理。

**判斷依據**：diff 中將 `jwt.verify(token, this.tinybirdConfig.adminToken)` 改為 `jwt.decode(token)`，移除了簽章驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> JWT 簽署時移除 `noTimestamp` 選項，可能影響 token 格式</summary>

原本 `jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true})` 明確指定不加入 `iat` 時間戳，現在改為 `jwt.sign(payload, this.tinybirdConfig.adminToken)`，會自動加入 `iat`。這可能影響 token 的 payload 結構，若 Tinybird 端預期沒有 `iat` 欄位，可能導致驗證失敗或行為改變。

**建議**：確認 Tinybird 端是否接受含有 `iat` 的 token，若不需要可保留 `noTimestamp: true`。

**判斷依據**：diff 中移除了 `{noTimestamp: true}` 選項。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13593 (cache hit 1408) ｜ completion tokens 1084 ｜ PR #12</sub>