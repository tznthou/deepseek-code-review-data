<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 v2 bookings API 的回應中新增 displayEmail / displayGuests 欄位，目的是移除 OAuth 產生的 CUID 後綴，提供乾淨的顯示用 email。主要風險在於 getDisplayEmail 使用固定長度 25 的 regex 移除後綴，若 CUID 長度或格式變更會失效；此外，移除 getOutputRecurringSeatedBookings 的排序可能改變 API 回應順序，影響依賴排序的客戶端。建議先確認 CUID 格式的穩定性，並評估排序移除的必要性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 的 regex 假設 CUID 長度固定為 25，未來可能失效 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除 getOutputRecurringSeatedBookings 的排序可能改變 API 回應順序 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:157` | displayGuests 的 map 回呼可能遺失 this 綁定 | 0.60 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:322` | displayGuests 的 map 回呼可能遺失 this 綁定（第二處） | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 的 regex 假設 CUID 長度固定為 25，未來可能失效</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除 email 中的 CUID 後綴。此 regex 假設 CUID 長度固定為 25 個英數字元。若 CUID 的產生方式變更（例如長度改變或包含其他字元），此函式將無法正確移除後綴，導致 displayEmail 仍包含 CUID。建議確認 CUID 的格式規範，並考慮使用更穩健的解析方式（例如從 email 的 local part 中分離出已知的 CUID 模式），或至少加入單元測試涵蓋不同長度的 CUID。

**判斷依據**：diff 中新增的 getDisplayEmail 方法，regex 明確指定 {25} 長度。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除 getOutputRecurringSeatedBookings 的排序可能改變 API 回應順序</summary>

原本 `getOutputRecurringSeatedBookings` 會依 `start` 時間排序回傳的 bookings，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回應的順序不穩定（取決於資料庫查詢的順序），影響依賴排序的客戶端。若排序是有意移除，請確認所有呼叫端都能接受任意順序；否則應保留排序。

**判斷依據**：diff 中刪除了 `return transformed.sort(...)` 並改為 `return transformed;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:157</code> displayGuests 的 map 回呼可能遺失 this 綁定</summary>

在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞 `this.getDisplayEmail` 作為回呼。若 `getDisplayEmail` 內部依賴 `this`（目前沒有，但未來可能加入），會導致執行時錯誤。建議改為 `(guest) => this.getDisplayEmail(guest)` 以確保綁定。

**判斷依據**：diff 中新增的 map 呼叫，直接使用 this.getDisplayEmail 作為回呼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:322</code> displayGuests 的 map 回呼可能遺失 this 綁定（第二處）</summary>

在 `getOutputRecurringBooking` 中，同樣使用 `bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)`，存在相同的 `this` 綁定風險。建議改為箭頭函式。

**判斷依據**：diff 中新增的 map 呼叫，但此處已使用箭頭函式，因此風險較低；仍建議統一。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12625 (cache hit 11136) ｜ completion tokens 1170 ｜ PR #4</sub>