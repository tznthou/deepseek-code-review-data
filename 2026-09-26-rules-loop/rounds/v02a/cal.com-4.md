<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 API v2 的預訂輸出中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 電子郵件中的 CUID 後綴（+25 位英數字）。主要風險在於 getDisplayEmail 使用固定長度 25 的正規表達式，若 CUID 長度或格式變更會失效；此外，移除 getOutputRecurringSeatedBookings 的排序可能改變既有 API 行為。整體而言，功能方向合理，但需確認正規表達式的正確性與排序移除的影響。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 的正規表達式假設 CUID 長度固定為 25，可能無法正確移除所有後綴 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除 getOutputRecurringSeatedBookings 的排序可能改變 API 回應順序 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:165` | 使用 this.getDisplayEmail 作為 Array.map 的回呼可能導致 this 綁定問題 | 0.60 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:60` | cleanEmailForDisplay 靜態方法與服務層的 getDisplayEmail 重複，可能造成維護不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 的正規表達式假設 CUID 長度固定為 25，可能無法正確移除所有後綴</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除電子郵件中的 CUID 後綴。此正規表達式假設 CUID 恰好為 25 個英數字元，但若 CUID 長度或格式變更（例如未來改為不同長度或包含其他字元），此函式將無法正確移除後綴，導致 displayEmail 仍包含 CUID。建議改為更彈性的模式，例如 `/\+[^@]+/` 或使用專案的 CUID 解析工具。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用固定長度 25 的正規表達式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除 getOutputRecurringSeatedBookings 的排序可能改變 API 回應順序</summary>

原本 `getOutputRecurringSeatedBookings` 會依開始時間排序結果，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回應的預訂順序不再按時間排序，影響依賴此順序的客戶端。若排序非必要，請確認移除的意圖；否則應保留排序。

**判斷依據**：diff 中刪除了 `return transformed.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());` 並改為 `return transformed;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:165</code> 使用 this.getDisplayEmail 作為 Array.map 的回呼可能導致 this 綁定問題</summary>

在 `bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 中，直接將 `this.getDisplayEmail` 作為回呼傳入 `map`。若 `getDisplayEmail` 內部依賴 `this`，則會因為 `this` 未綁定而失敗。目前 `getDisplayEmail` 未使用 `this`，因此暫時安全，但未來若修改方法內容可能引入 bug。建議改為箭頭函式：`map((guest) => this.getDisplayEmail(guest))`。

**判斷依據**：diff 中新增的程式碼直接傳遞 this.getDisplayEmail 給 map。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:60</code> cleanEmailForDisplay 靜態方法與服務層的 getDisplayEmail 重複，可能造成維護不一致</summary>

在 `BookingAttendee` 類別中新增了靜態方法 `cleanEmailForDisplay`，其邏輯與 `OutputBookingsService_2024_08_13` 中的 `getDisplayEmail` 完全相同。這導致程式碼重複，未來若需修改清理邏輯，需同時更新兩處。建議將此邏輯抽成共用工具函式，或僅保留一處。

**判斷依據**：diff 中新增的靜態方法與 output.service.ts 中的 getDisplayEmail 邏輯重複。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12625 (cache hit 1536) ｜ completion tokens 1226 ｜ PR #4</sub>