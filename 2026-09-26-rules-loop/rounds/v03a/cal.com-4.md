<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 API v2 的預訂輸出中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 後綴（+25 字元）以提供乾淨的顯示用電子郵件。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪合法電子郵件中的加號部分；此外，移除排序邏輯可能導致輸出順序不穩定，且新增欄位為必填可能造成 API 相容性問題。建議先修正正規表達式並確認排序移除的影響。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97` | getDisplayEmail 正規表達式可能誤刪合法電子郵件中的加號部分 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序可能導致輸出順序不穩定 | 0.70 |
| ⚠️ | Major | `docs/api-reference/v2/openapi.json:31715` | 新增必填欄位可能破壞 API 相容性 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:157` | displayGuests 使用 map 時未正確綁定 this | 0.60 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 未處理 null 或非字串輸入 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97</code> getDisplayEmail 正規表達式可能誤刪合法電子郵件中的加號部分</summary>

`getDisplayEmail` 使用 `email.replace(/\+[a-zA-Z0-9]{25}/, "")` 移除加號後綴，但此正規表達式會匹配任何加號後接 25 個字母或數字的模式，不限於 OAuth 後綴。例如 `user+tag@example.com` 中的 `+tag` 若長度為 25 個字元（如 `user+abcdefghijklmnopqrstuvwxyz@example.com`）也會被移除，導致顯示錯誤的電子郵件。建議改用更精確的模式，例如僅匹配已知的 OAuth 後綴格式（如 `+[a-zA-Z0-9]{25}@` 或使用後綴白名單），或先驗證後綴是否為系統產生的格式。

**判斷依據**：diff 中新增的 getDisplayEmail 方法，正規表達式未限制後綴的來源或格式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序可能導致輸出順序不穩定</summary>

在 `getOutputRecurringSeatedBookings` 中，原本有依 `start` 時間排序的邏輯，但此 PR 將其移除（`return transformed;` 取代排序後的陣列）。這可能導致 API 回傳的預訂順序不固定，影響前端顯示或測試的穩定性。若排序並非必要，請確認移除的意圖；否則應保留排序或提供明確的排序依據。

**判斷依據**：diff 中刪除了 `return transformed.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());` 並改為直接回傳。

</details>

<details><summary>⚠️ <b>Major</b> — <code>docs/api-reference/v2/openapi.json:31715</code> 新增必填欄位可能破壞 API 相容性</summary>

在 OpenAPI 規格中，`displayEmail` 被加入多個 schema 的 `required` 陣列（例如 `BookingHost`、`BookingAttendee` 等）。這表示 API 消費者必須處理此新欄位，但若既有客戶端未預期此欄位，可能導致解析錯誤或型別不符。建議將 `displayEmail` 標記為可選（非必填），或提供版本相容策略。

**判斷依據**：diff 中多處將 `displayEmail` 加入 `required` 陣列。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:157</code> displayGuests 使用 map 時未正確綁定 this</summary>

在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 直接傳遞 `this.getDisplayEmail` 作為 callback，但 `getDisplayEmail` 內部未使用 `this`，因此目前不會出錯。然而，若未來該方法改為依賴 `this`，此處會因 `this` 為 `undefined` 而失敗。建議改為 `map((guest) => this.getDisplayEmail(guest))` 以保持一致性（在 `getOutputRecurringBooking` 中已使用箭頭函式）。

**判斷依據**：diff 中 `getOutputBooking` 的 guests 處理使用 `map(this.getDisplayEmail)`，而 `getOutputRecurringBooking` 使用 `map((guest: string) => this.getDisplayEmail(guest))`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 未處理 null 或非字串輸入</summary>

`getDisplayEmail` 的參數型別為 `string`，但呼叫處可能傳入 `undefined` 或 `null`（例如 `attendee.email` 可能為空）。雖然目前呼叫前有條件檢查，但若未來有其他呼叫點未檢查，可能導致執行時錯誤。建議在方法內加入防禦性檢查，或使用更嚴格的型別。

**判斷依據**：diff 中方法定義未處理非字串輸入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12635 (cache hit 11136) ｜ completion tokens 1521 ｜ PR #4</sub>