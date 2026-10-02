<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在訂位輸出中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 郵件中的 CUID 後綴（+25 字元）。主要風險在於正規表達式 /\+[a-zA-Z0-9]{25}/ 可能誤刪合法郵件中的加號標籤，且未涵蓋所有輸出路徑（如 getOutputRecurringSeatedBookings 移除了排序，可能影響既有行為）。此外，OpenAPI 文件中的縮排變更可能造成格式不一致。建議先修正郵件清理邏輯，並確認所有輸出端點都一致套用。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 的正規表達式可能誤刪合法郵件中的加號標籤 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除 getOutputRecurringSeatedBookings 的排序可能影響輸出順序 | 0.70 |
| 🔸 | Minor | `docs/api-reference/v2/openapi.json:31726` | OpenAPI 文件中的縮排變更可能造成格式不一致 | 0.60 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:154` | displayGuests 的 map 回呼可能遺失 this 綁定 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 的正規表達式可能誤刪合法郵件中的加號標籤</summary>

`getDisplayEmail` 使用 `email.replace(/\+[a-zA-Z0-9]{25}/, "")` 來移除 CUID 後綴，但此正規表達式會匹配任何 `+` 後接 25 個字母或數字的模式，而不僅限於 CUID。例如 `user+tag@example.com` 中的 `+tag` 若長度為 25 字元，也會被移除，導致顯示錯誤的郵件地址。建議使用更精確的模式，例如僅匹配已知的 CUID 格式（如 `+[a-z0-9]{25}` 且需為小寫），或改用其他方式（如從資料庫取得原始郵件）來取得顯示郵件。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用正規表達式 /\+[a-zA-Z0-9]{25}/，此模式可能匹配非 CUID 的加號標籤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除 getOutputRecurringSeatedBookings 的排序可能影響輸出順序</summary>

在 `getOutputRecurringSeatedBookings` 中，原本有 `return transformed.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());`，但此 PR 將其改為 `return transformed;`，移除了排序。這可能導致回傳的訂位順序不再按開始時間排序，影響前端顯示或依賴順序的邏輯。若排序是有意移除，請確認所有呼叫端都能接受任意順序；否則應保留排序。

**判斷依據**：diff 中將原本的 sort 邏輯移除，改為直接回傳 transformed。

</details>

<details><summary>🔸 <b>Minor</b> — <code>docs/api-reference/v2/openapi.json:31726</code> OpenAPI 文件中的縮排變更可能造成格式不一致</summary>

在 openapi.json 中，多處 `"required"` 陣列的縮排從原本的 8 空格改為無縮排（例如 `"required": [` 前少了空格），這可能導致 JSON 格式不一致，影響可讀性或工具解析。建議檢查並修正縮排，使其與檔案其他部分一致。

**判斷依據**：diff 中顯示多處 `"required"` 的縮排被移除，例如原本為 `        "required": [` 改為 `"required": [`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:154</code> displayGuests 的 map 回呼可能遺失 this 綁定</summary>

在 `bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 中，直接傳遞 `this.getDisplayEmail` 作為 map 的回呼，若 `getDisplayEmail` 內部使用 `this`，則會因為失去綁定而導致錯誤。目前 `getDisplayEmail` 未使用 `this`，但未來若修改可能造成問題。建議改為箭頭函式 `(guest) => this.getDisplayEmail(guest)` 以確保綁定。

**判斷依據**：diff 中顯示使用 `this.getDisplayEmail` 作為 map 回呼，未使用箭頭函式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12625 (cache hit 12544) ｜ completion tokens 1235 ｜ PR #4</sub>