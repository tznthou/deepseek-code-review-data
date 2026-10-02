<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 API v2 的 booking 輸出中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 郵件中的 CUID 後綴。主要風險在於 getDisplayEmail 使用固定長度 25 的 regex 來移除後綴，若 CUID 長度未來變動或郵件格式不同，可能無法正確清理或誤刪合法字元。此外，移除 recurring seated bookings 的排序可能導致輸出順序不穩定。整體變更範圍明確，測試涵蓋主要情境，但建議修正 regex 的脆弱性並確認排序移除的影響。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97` | getDisplayEmail 的 regex 過於脆弱，可能無法正確移除 CUID 後綴 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除 recurring seated bookings 的排序可能導致輸出順序不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97</code> getDisplayEmail 的 regex 過於脆弱，可能無法正確移除 CUID 後綴</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除 CUID 後綴，但 CUID 的長度可能不是固定 25 個字元，或未來可能變更。若長度不同，此 regex 將無法匹配，導致 displayEmail 仍包含後綴；若郵件 local part 中出現符合此模式的合法字串（例如 `user+1234567890123456789012345@example.com`），也會被誤刪。建議改用更精確的 CUID 格式（例如 `/\+[a-z0-9]{25}/i` 或直接使用 CUID 驗證函式），或從資料來源直接取得原始郵件，避免依賴字串操作。

**判斷依據**：diff 中新增的 `getDisplayEmail` 方法，使用固定長度 25 的 regex。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除 recurring seated bookings 的排序可能導致輸出順序不穩定</summary>

原本 `getOutputRecurringSeatedBookings` 會依 `start` 時間排序，但此 PR 移除了排序邏輯，直接回傳 `transformed`。若 `bookingsIds` 的順序未保證依時間排序，API 回傳的陣列順序可能不穩定，影響前端顯示或測試。建議確認呼叫端是否已排序，或保留排序以維持既有行為。

**判斷依據**：diff 中將 `return transformed.sort(...)` 改為 `return transformed;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11810 (cache hit 11136) ｜ completion tokens 690 ｜ PR #4</sub>