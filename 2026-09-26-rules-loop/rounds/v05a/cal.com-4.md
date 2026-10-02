<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 v2 bookings API 的回應中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 後綴（+25 字元）以提供乾淨的顯示用 email。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪合法 email 中的加號部分；此外，移除排序邏輯可能導致回傳順序不穩定，且新增欄位為必填可能造成向後相容性問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序邏輯可能導致回傳順序不穩定 | 0.70 |
| ⚠️ | Major | `docs/api-reference/v2/openapi.json:31715` | 新增必填欄位可能造成向後相容性問題 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:164` | displayGuests 的 map 回呼可能遺失 this 綁定 | 0.60 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:318` | displayGuests 的 map 回呼型別不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除後綴，但此模式會匹配任何 email 中加號後緊接 25 個英數字的片段。若使用者的 email 本身包含加號（例如 `john+work@example.com`），且加號後的字串長度剛好為 25 個英數字，則會被錯誤移除。建議改用更精確的模式，例如只移除符合特定格式（如 CUID）的後綴，或使用更嚴格的邊界條件。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用正規表達式 /\+[a-zA-Z0-9]{25}/，未考慮 email 中原本就存在加號的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序邏輯可能導致回傳順序不穩定</summary>

原本 `getOutputRecurringSeatedBookings` 會依開始時間排序，但此 PR 移除了排序，直接回傳 `transformed`。這可能導致 API 回傳的預訂順序不固定，影響前端顯示或測試的穩定性。若排序並非必要，應在 PR 描述中說明原因；否則建議保留排序。

**判斷依據**：diff 中將原本的排序邏輯 `return transformed.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());` 改為 `return transformed;`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>docs/api-reference/v2/openapi.json:31715</code> 新增必填欄位可能造成向後相容性問題</summary>

在 OpenAPI 規格中，`displayEmail` 被加入多個 schema 的 `required` 陣列，但此欄位是新增的。若既有客戶端依賴舊的 schema 驗證，可能會因為缺少此欄位而失敗。建議將 `displayEmail` 標記為選用（非 required），或提供預設值，以維持向後相容性。

**判斷依據**：diff 中在 required 陣列新增了 "displayEmail"。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:164</code> displayGuests 的 map 回呼可能遺失 this 綁定</summary>

在 `bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 中，直接傳遞 `this.getDisplayEmail` 作為 map 的回呼。若 `getDisplayEmail` 內部使用 `this`，則會因為失去綁定而拋出錯誤。目前 `getDisplayEmail` 未使用 `this`，但未來若修改可能造成問題。建議改為 `map((guest) => this.getDisplayEmail(guest))` 以確保安全。

**判斷依據**：diff 中出現 `map(this.getDisplayEmail)` 的寫法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:318</code> displayGuests 的 map 回呼型別不一致</summary>

在另一個方法中，`displayGuests` 的 map 回呼使用了箭頭函式 `(guest: string) => this.getDisplayEmail(guest)`，與前一個方法不一致。雖然功能相同，但建議統一寫法以提升可讀性。

**判斷依據**：diff 中出現兩種不同的 map 回呼寫法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12594 (cache hit 11136) ｜ completion tokens 1376 ｜ PR #4</sub>