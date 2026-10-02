<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 v2 bookings API 的回應中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 產生的 CUID 後綴（+25 字元）以提供乾淨的顯示用 email。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪合法 email 中的加號部分；此外，移除 getOutputRecurringSeatedBookings 的排序邏輯可能導致回傳順序不穩定，影響前端顯示。建議先修正 email 清理邏輯並確認排序移除的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除 getOutputRecurringSeatedBookings 的排序可能導致回傳順序不穩定 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:165` | displayGuests 的 map 回呼可能遺失 this 綁定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除 CUID 後綴，但此模式會匹配任何 email 中出現的 `+` 後接 25 個英數字元的片段。若使用者的 email 本身包含加號（例如 `user+tag@example.com`），且 `tag` 恰好為 25 個英數字元，則該部分會被錯誤移除，導致顯示錯誤的 email。

**失敗情境**：使用者 email 為 `john+abcdefghijklmnopqrstuvwxyz12345@example.com`（加號後 25 個字元），`getDisplayEmail` 會回傳 `john@example.com`，而非原始 email。

**建議**：改為更精確的比對，例如僅在 email 的 local part 中比對 CUID 格式（如 `/\+[a-zA-Z0-9]{25}@/`），或使用已知的 CUID 產生規則來驗證。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用寬鬆的正規表達式，未限制加號後綴的位置或格式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除 getOutputRecurringSeatedBookings 的排序可能導致回傳順序不穩定</summary>

原本 `getOutputRecurringSeatedBookings` 會依 `start` 時間排序回傳的 bookings，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳的 recurring bookings 順序不固定，影響前端顯示或測試的穩定性。

**失敗情境**：若資料庫回傳的 bookings 順序未依時間排序，前端可能顯示錯誤的順序，或依賴順序的測試（如 e2e）會 flaky。

**建議**：除非有明確理由，否則應保留排序邏輯，或確認呼叫端已自行排序。

**判斷依據**：diff 中刪除了 `return transformed.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());`，改為直接回傳 `transformed`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:165</code> displayGuests 的 map 回呼可能遺失 this 綁定</summary>

在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 直接傳遞 `this.getDisplayEmail` 作為回呼，但 `getDisplayEmail` 是實例方法，若其內部依賴 `this`（目前沒有），未來修改可能導致錯誤。此外，在其他方法中使用了箭頭函式包裝，此處不一致。

**建議**：統一使用箭頭函式，例如 `.map((guest: string) => this.getDisplayEmail(guest))`，以避免潛在的 `this` 綁定問題。

**判斷依據**：diff 中此處直接傳遞方法參考，而其他類似處使用箭頭函式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11186 (cache hit 11136) ｜ completion tokens 1151 ｜ PR #4</sub>