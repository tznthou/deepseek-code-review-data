<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 API 回應新增 displayEmail 欄位，以去除 OAuth 後綴（CUID），並更新相關測試與 OpenAPI 規格。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪合法電子郵件中的加號部分；此外，移除排序邏輯可能導致輸出順序不穩定，且新增欄位為必填可能造成向後相容性問題。建議先修正正規表達式並確認排序移除的影響。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表達式可能誤刪合法電子郵件中的加號部分 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序可能導致輸出順序不穩定 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:134` | displayEmail 為必填可能造成向後相容性問題 | 0.60 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:157` | 使用 map 傳遞方法參考可能導致 this 綁定問題 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表達式可能誤刪合法電子郵件中的加號部分</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除加號後綴，但此模式會匹配任何加號後跟 25 個字母數字的字串，不限於 CUID 後綴。若使用者電子郵件本身包含加號（例如 `user+tag@example.com`），且 `tag` 長度為 25 個字母數字，則會被錯誤移除。建議使用更精確的模式，例如 `/\+[a-zA-Z0-9]{25}@/` 或先驗證後綴格式。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用寬鬆的正規表達式，未限制後綴必須在 @ 之前，可能誤刪合法電子郵件中的加號部分。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序可能導致輸出順序不穩定</summary>

原本 `getOutputRecurringSeatedBookings` 會依開始時間排序，但此 PR 移除了排序邏輯，直接回傳 `transformed`。若 `bookingsIds` 的順序未保證按時間排序，API 回應的順序可能不穩定，影響客戶端依賴。建議保留排序或確認呼叫端已排序。

**判斷依據**：diff 中將原本的排序邏輯 `return transformed.sort(...)` 改為 `return transformed;`，移除了排序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:134</code> displayEmail 為必填可能造成向後相容性問題</summary>

新增的 `displayEmail` 欄位在 TypeScript 類別中宣告為非可選（`displayEmail!: string`），且在 OpenAPI 規格中列為 required。若現有客戶端未預期此欄位，可能導致解析錯誤。建議考慮設為可選或提供預設值。

**判斷依據**：在 booking.output.ts 中新增的 displayEmail 欄位沒有 `?` 標記，且 OpenAPI 規格將其列為 required。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:157</code> 使用 map 傳遞方法參考可能導致 this 綁定問題</summary>

在 `bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 中，直接將 `this.getDisplayEmail` 作為回呼傳遞給 `map`，若 `getDisplayEmail` 內部使用 `this`，則會丟失綁定。目前方法未使用 `this`，但未來修改可能引入問題。建議改為箭頭函數 `(guest) => this.getDisplayEmail(guest)`。

**判斷依據**：diff 中此處直接傳遞方法參考，未綁定 this。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12635 (cache hit 12544) ｜ completion tokens 1116 ｜ PR #4</sub>