<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Tinybird 中未使用的 device、browser、os 過濾條件，並更新了相關測試。主要風險在於 TinybirdService.js 中 JWT 處理的變更：`_serverToken` 現在儲存整個 token 物件而非 token 字串，且 `_isJWTExpired` 改用 `jwt.decode` 而非 `jwt.verify`，這可能導致使用過期或無效 token 的風險。此外，`_generateToken` 移除了 `noTimestamp: true` 選項，可能影響 token 的時效性。建議優先修正 JWT 相關變更，並確認移除過濾條件後沒有其他程式碼仍依賴這些參數。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:98` | JWT token 儲存型別錯誤導致後續使用失效 | 0.95 |
| 🛑 | Blocker | `ghost/core/core/server/services/tinybird/TinybirdService.js:164` | 使用 jwt.decode 取代 jwt.verify 導致無法驗證 token 有效性 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/tinybird/TinybirdService.js:147` | 移除 noTimestamp 選項可能導致 token 包含 iat 欄位 | 0.80 |
| ⚠️ | Major | `ghost/core/core/server/data/tinybird/endpoints/api_kpis.pipe:143` | 移除 device、browser、os 過濾條件可能影響 API 相容性 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/data/tinybird/tests/api_top_locations.yaml:73` | 測試參數變更可能未覆蓋原有過濾條件 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:98</code> JWT token 儲存型別錯誤導致後續使用失效</summary>

`_serverToken` 原本儲存 token 字串，現在改為儲存整個 token 物件（`{token, exp}`）。但在 `getToken` 方法中，回傳值仍使用 `this._serverToken`，這會導致回傳物件而非字串，可能造成呼叫端錯誤。建議改為 `this._serverToken = tokenData.token;` 或調整回傳邏輯。

**判斷依據**：diff 中將 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`，但後續回傳仍為 `this._serverToken`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:164</code> 使用 jwt.decode 取代 jwt.verify 導致無法驗證 token 有效性</summary>

`_isJWTExpired` 原本使用 `jwt.verify` 來驗證 token 的簽名和有效性，現在改用 `jwt.decode` 僅解碼而不驗證。這可能導致接受無效或過期的 token，造成安全風險。建議保留 `jwt.verify`，或明確說明為何不需要驗證。

**判斷依據**：diff 中將 `jwt.verify(token, this.tinybirdConfig.adminToken)` 改為 `jwt.decode(token)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/tinybird/TinybirdService.js:147</code> 移除 noTimestamp 選項可能導致 token 包含 iat 欄位</summary>

`jwt.sign` 原本使用 `{noTimestamp: true}` 來避免在 payload 中加入 `iat`（issued at）欄位。移除後，token 將包含 `iat`，這可能影響某些依賴 payload 結構的邏輯，或導致不必要的時間戳。建議確認是否需要保留此選項。

**判斷依據**：diff 中移除了 `{noTimestamp: true}` 選項。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/data/tinybird/endpoints/api_kpis.pipe:143</code> 移除 device、browser、os 過濾條件可能影響 API 相容性</summary>

這些過濾條件被移除後，若前端或其他服務仍傳遞這些參數，將被忽略，可能導致資料不正確。建議確認所有呼叫端都已更新，或保留參數但標記為 deprecated。

**判斷依據**：diff 中刪除了 device、browser、os 的過濾條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/data/tinybird/tests/api_top_locations.yaml:73</code> 測試參數變更可能未覆蓋原有過濾條件</summary>

將測試參數從 device/browser 改為 source/pathname，但未新增對應的測試案例來驗證移除過濾條件後的行為。建議補充測試以確保功能正常。

**判斷依據**：diff 中修改了測試參數，但未新增測試案例。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15938 (cache hit 15872) ｜ completion tokens 1230 ｜ PR #12</sub>