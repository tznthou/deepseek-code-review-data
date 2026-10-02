<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 API v2 的預訂輸出中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 後綴（CUID）以提供乾淨的顯示用電子郵件。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪一般電子郵件中的加號部分；此外，移除排序邏輯可能導致輸出順序不穩定，且新增欄位為必填可能造成既有 API 用戶端的相容性問題。建議先修正正規表達式並確認排序移除的影響。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97` | getDisplayEmail 正規表達式可能誤刪一般電子郵件中的加號部分 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序可能導致輸出順序不穩定 | 0.70 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:32` | 新增必填欄位可能造成 API 相容性問題 | 0.60 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 未處理 null 或非字串輸入 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97</code> getDisplayEmail 正規表達式可能誤刪一般電子郵件中的加號部分</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除後綴，但此模式會匹配任何加號後接 25 個英數字的字串。若使用者的電子郵件本身包含加號（例如 `user+tag@example.com`），且 `tag` 長度為 25 個英數字，則會被誤刪。建議改用更精確的模式，例如僅匹配已知的 CUID 格式（如 `/\+[a-z0-9]{25}@/` 或使用 `cuid` 套件驗證），或先確認後綴是否為 CUID 再移除。

**判斷依據**：diff 中新增的 `getDisplayEmail` 方法使用寬鬆的正規表達式，可能影響合法電子郵件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序可能導致輸出順序不穩定</summary>

原本 `getOutputRecurringSeatedBookings` 會依開始時間排序，但此 PR 移除了排序邏輯。若資料庫回傳的順序不保證按時間排序，API 回應的陣列順序可能不穩定，影響前端顯示或測試。建議保留排序，或確認資料庫查詢已保證順序。

**判斷依據**：diff 中將 `return transformed.sort(...)` 改為 `return transformed;`，移除了排序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:32</code> 新增必填欄位可能造成 API 相容性問題</summary>

在 `BookingAttendee`、`BookingHost` 等 DTO 中新增 `displayEmail` 並標記為必填（`@IsString()` 且無 `@IsOptional()`），這會使 API 回應的 schema 變更。若既有用戶端依賴舊 schema，可能因缺少該欄位而解析失敗。建議評估是否應設為選用，或提供相容性策略。

**判斷依據**：diff 中新增 `displayEmail` 欄位且未標記為可選。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 未處理 null 或非字串輸入</summary>

`getDisplayEmail` 假設輸入為字串，但呼叫處可能傳入 `undefined` 或 `null`（例如 `attendee.email` 可能為空）。若電子郵件缺失，會拋出錯誤。建議加入型別檢查或使用可選串連。

**判斷依據**：方法簽名未允許 null/undefined，但呼叫處可能傳入空值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12615 (cache hit 12544) ｜ completion tokens 1045 ｜ PR #4</sub>