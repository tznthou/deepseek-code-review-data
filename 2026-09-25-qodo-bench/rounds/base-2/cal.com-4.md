<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 v2 訂位 API 的回應中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 後綴（+25 字元）以提供乾淨的顯示用 email。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪合法 email 中的加號後綴；此外，移除排序邏輯可能導致回傳順序不穩定，且新增欄位為必填可能造成既有 API 用戶端相容性問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表達式可能誤刪合法 email 中的加號後綴 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序邏輯可能導致回傳順序不穩定 | 0.70 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:32` | 新增必填欄位可能造成 API 相容性問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表達式可能誤刪合法 email 中的加號後綴</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除後綴，但此模式會匹配任何 email 中長度為 25 的加號後綴，而不僅限於 OAuth 後綴。例如 `user+abcdefghijklmnopqrstuvwxyz@example.com` 會被錯誤地轉換為 `user@example.com`，導致顯示錯誤的 email。建議使用更精確的模式，例如僅匹配已知的 OAuth 後綴格式，或使用更嚴格的邊界條件（如 `$` 或 `@` 前）。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用寬鬆的正規表達式，未限制後綴的上下文。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序邏輯可能導致回傳順序不穩定</summary>

在 `getOutputRecurringSeatedBookings` 中，原本依 `start` 時間排序的邏輯被移除，直接回傳 `transformed`。這可能導致 API 回傳的訂位順序不穩定，影響前端顯示或測試的可靠性。若排序是有意移除，請確認是否有其他機制保證順序；否則建議保留排序。

**判斷依據**：diff 中刪除了 `return transformed.sort(...)` 並改為 `return transformed;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:32</code> 新增必填欄位可能造成 API 相容性問題</summary>

在 `BookingAttendee`、`BookingHost`、`ReassignedToDto` 等類別中新增 `displayEmail` 欄位，且未標記為可選（`@IsOptional()`）。這會使 API 回應的 schema 將該欄位列為必填，可能導致既有用戶端在解析回應時因缺少該欄位而失敗。若此欄位為新增且應向後相容，建議標記為可選或提供預設值。

**判斷依據**：diff 中新增的 displayEmail 欄位未使用 @IsOptional()，且 openapi.json 中將其加入 required 陣列。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11186 (cache hit 11136) ｜ completion tokens 927 ｜ PR #4</sub>