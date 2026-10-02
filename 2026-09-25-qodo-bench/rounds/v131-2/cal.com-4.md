<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 2024-08-13 版本的訂位 API 新增 displayEmail 與 displayGuests 欄位，目的是回傳去除 OAuth 後綴（+25 字元）的乾淨 email 供顯示用。主要變更在 output.service.ts 中新增 getDisplayEmail 方法，並在多個輸出物件中套用。整體風險中等：正規表達式可能誤刪合法 email 中的加號後綴，且移除排序邏輯可能影響既有行為。建議先修正 email 清理邏輯，並確認排序移除的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表達式可能誤刪合法 email 中的加號後綴 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序邏輯可能導致回傳順序不穩定 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:160` | displayGuests 使用 map 時未綁定 this 可能導致錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表達式可能誤刪合法 email 中的加號後綴</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除 email 中加號後綴。但此正規表達式會匹配任何 email 中長度為 25 的字母數字序列，即使該序列並非 OAuth 後綴。例如 `user+abcdefghijklmnopqrstuvwxy@example.com` 會被錯誤改為 `user@example.com`。此外，若 email 中有多個符合條件的片段，只會移除第一個。建議改用更精確的規則，例如僅移除已知的 OAuth 後綴格式（如 `+[a-z0-9]{25}` 且位於 @ 之前），或使用白名單方式。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用正規表達式 /\+[a-zA-Z0-9]{25}/，可能誤刪合法 email 中的加號後綴。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序邏輯可能導致回傳順序不穩定</summary>

`getOutputRecurringSeatedBookings` 原本會依開始時間排序，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳的訂位順序不穩定，影響前端顯示或測試。若排序並非必要，請確認移除原因；否則應保留排序。

**判斷依據**：diff 中將原本的排序邏輯 `return transformed.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());` 改為 `return transformed;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:160</code> displayGuests 使用 map 時未綁定 this 可能導致錯誤</summary>

在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 直接傳遞 `this.getDisplayEmail` 作為 callback，但 `getDisplayEmail` 並未使用 `this`，因此目前不會出錯。然而，若未來方法內使用 `this`，可能導致錯誤。建議改為 `(guest: string) => this.getDisplayEmail(guest)` 以保持一致。

**判斷依據**：diff 中在 getOutputBooking 方法內使用 `this.getDisplayEmail` 作為 map callback，未綁定 this。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11150 (cache hit 11136) ｜ completion tokens 989 ｜ PR #4</sub>