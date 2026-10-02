<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 在 v2 bookings API 的回應中新增 displayEmail / displayGuests 欄位，目的是移除 OAuth 郵件中的 CUID 後綴以供顯示。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪一般郵件中的加號別名；此外移除排序邏輯可能造成行為回歸，且部分測試期望值與實作不一致。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表達式可能誤刪合法郵件中的加號別名 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序邏輯可能導致輸出順序不穩定 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/e2e/managed-user-bookings.e2e-spec.ts:651` | 測試期望值與實作不一致：displayEmail 應為原始郵件而非去除後綴 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:165` | displayGuests 使用 map 時未綁定 this，可能導致錯誤 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:318` | displayGuests 使用 map 時未綁定 this，可能導致錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表達式可能誤刪合法郵件中的加號別名</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除 CUID 後綴，但此模式會匹配任何長度為 25 的字母數字序列，即使它不是 CUID。例如 `user+abcdefghijklmnopqrstuvwxyz@example.com` 會被錯誤地轉換為 `user@example.com`。這可能導致顯示的郵件與實際郵件不符，造成混淆或資料遺失。建議使用更精確的 CUID 格式（例如 `/\+[a-z0-9]{25}/` 或明確的 CUID 前綴），或改用其他方式識別並移除後綴。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用寬鬆的正規表達式，未限制為 CUID 格式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序邏輯可能導致輸出順序不穩定</summary>

在 `getOutputRecurringSeatedBookings` 中，原本會依開始時間排序的邏輯被移除，改為直接回傳 `transformed`。這可能導致 API 回傳的預約順序不穩定，影響前端顯示或測試。若排序是有意移除，請確認不會影響相依功能；否則應保留排序。

**判斷依據**：diff 中刪除了排序程式碼，直接回傳未排序的陣列。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/e2e/managed-user-bookings.e2e-spec.ts:651</code> 測試期望值與實作不一致：displayEmail 應為原始郵件而非去除後綴</summary>

在 `displayEmail fields` 測試中，`expect(bookingData.hosts[0].displayEmail).toEqual(firstManagedUserEmail);` 期望 displayEmail 等於 `firstManagedUserEmail`，但根據實作，displayEmail 是從 email 移除 CUID 後綴的結果。若 `firstManagedUserEmail` 是原始郵件（含後綴），此測試會失敗；若它是去除後綴的郵件，則測試名稱與變數命名可能造成混淆。請確認測試資料與實作一致。

**判斷依據**：diff 中新增的測試期望 displayEmail 等於 firstManagedUserEmail，但實作會移除 CUID 後綴。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:165</code> displayGuests 使用 map 時未綁定 this，可能導致錯誤</summary>

在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 直接傳遞 `this.getDisplayEmail` 作為 callback，但未綁定 `this`。若 `getDisplayEmail` 內部使用 `this`，會導致錯誤；目前實作未使用 `this`，但未來修改可能引入問題。建議改為 `map((guest) => this.getDisplayEmail(guest))` 以確保安全。

**判斷依據**：diff 中新增的 map 呼叫直接使用 this.getDisplayEmail，未綁定 this。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:318</code> displayGuests 使用 map 時未綁定 this，可能導致錯誤</summary>

在 `getOutputRecurringBooking` 中，同樣使用 `map(this.getDisplayEmail)`，未綁定 `this`。建議改為 arrow function 以確保安全。

**判斷依據**：diff 中新增的 map 呼叫直接使用 this.getDisplayEmail，未綁定 this。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12615 (cache hit 11136) ｜ completion tokens 1392 ｜ PR #4</sub>