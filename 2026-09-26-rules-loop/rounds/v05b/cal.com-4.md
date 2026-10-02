<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 2024-08-13 版本的 booking API 輸出中新增 displayEmail 與 displayGuests 欄位，目的是移除 email 中的 CUID 後綴以供顯示。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪合法 email 中的加號部分；此外，移除 recurring seated bookings 的排序可能改變既有 API 行為。建議先修正 email 清理邏輯並確認排序移除的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97` | getDisplayEmail 的正規表達式可能誤刪合法 email 中的加號部分 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除 recurring seated bookings 的排序可能改變 API 回應順序 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:167` | displayGuests 的 map 回呼可能遺失 this 綁定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97</code> getDisplayEmail 的正規表達式可能誤刪合法 email 中的加號部分</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除 CUID 後綴，但此模式會匹配任何 email 中加號後緊接 25 個字母或數字的片段。若使用者的 email 本身包含加號（例如 `user+tag@example.com`），且 tag 長度為 25 個字元，則該 tag 會被錯誤移除，導致顯示的 email 與實際不符。建議改用更精確的 CUID 格式（例如 `/\+[a-z0-9]{25}$/` 或直接使用 CUID 驗證函式），或僅在 email 的 local part 結尾處移除。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用寬鬆的正規表達式，未限制加號後綴的位置或格式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除 recurring seated bookings 的排序可能改變 API 回應順序</summary>

原本 `getOutputRecurringSeatedBookings` 會依開始時間排序結果，此 PR 移除了排序邏輯，直接回傳依輸入 ID 順序轉換的陣列。這可能導致前端依賴時間排序的顯示錯亂，或破壞既有 API 合約。若排序非必要，請確認所有呼叫端皆能接受任意順序；否則應保留排序。

**判斷依據**：diff 中刪除了 `return transformed.sort(...)` 並改為 `return transformed;`，且未提供任何說明。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:167</code> displayGuests 的 map 回呼可能遺失 this 綁定</summary>

在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞方法參考，若 `getDisplayEmail` 內部依賴 `this`（目前沒有），未來修改可能導致錯誤。建議改為箭頭函式 `(guest) => this.getDisplayEmail(guest)` 以確保綁定。

**判斷依據**：diff 中該行使用 `this.getDisplayEmail` 作為 map 回呼，未綁定 this。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12594 (cache hit 12544) ｜ completion tokens 896 ｜ PR #4</sub>