<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將錄音與逐字稿端點改為需要驗證，並更新權限與守衛設定，同時新增對應的 e2e 測試。主要風險在於錄音端點的權限從 BOOKING_READ 改為 BOOKING_WRITE，可能造成授權不足；此外，getRecordings 的呼叫移除了 await，若該方法回傳 Promise 將導致回傳資料型別錯誤。建議先確認權限變更的意圖，並修正 await 問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，可能回傳 Promise 而非資料 | 0.95 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能導致授權不足 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238` | 逐字稿端點守衛順序可能影響錯誤回應 | 0.70 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 未使用的 import BookingRepository | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，可能回傳 Promise 而非資料</summary>

在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫移除了 `await`。若 `getRecordings` 是非同步方法（回傳 Promise），則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這會導致 API 回傳錯誤的資料型別，前端可能無法正確處理。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件（序列化後可能變成空物件或錯誤），而非錄音清單。

**建議**：恢復 `await`，確保取得實際資料。

**判斷依據**：diff 中此行由 `const recordings = await this.calVideoService.getRecordings(bookingUid);` 改為 `const recordings = this.calVideoService.getRecordings(bookingUid);`，移除了 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能導致授權不足</summary>

錄音端點原本使用 `@Permissions([BOOKING_READ])`，現在改為 `@Permissions([BOOKING_WRITE])`。這表示只有具備寫入權限的 API 金鑰才能存取錄音，而一般唯讀金鑰將無法使用此端點。若此變更非刻意為之，可能造成現有整合失效。

**失敗情境**：使用僅有讀取權限的 API 金鑰呼叫此端點時，會收到 403 Forbidden。

**建議**：確認此權限變更是否符合預期。若錄音僅需讀取權限，應維持 `BOOKING_READ`。

**判斷依據**：diff 中此行由 `@Permissions([BOOKING_READ])` 改為 `@Permissions([BOOKING_WRITE])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238</code> 逐字稿端點守衛順序可能影響錯誤回應</summary>

逐字稿端點的 `@UseGuards` 順序從原本的 `BookingUidGuard` 改為 `BookingPbacGuard, ApiAuthGuard, BookingUidGuard`。守衛執行順序可能影響錯誤回應的優先權。例如，若 `BookingPbacGuard` 在 `ApiAuthGuard` 之前執行，未驗證的請求可能先觸發 Pbac 檢查而回傳 403，而非預期的 401。

**失敗情境**：未帶憑證的請求可能收到 403 而非 401，影響客戶端錯誤處理。

**建議**：確認守衛順序是否符合預期，通常應先執行驗證守衛（ApiAuthGuard）再執行授權守衛（BookingPbacGuard）。

**判斷依據**：diff 中此行由 `@UseGuards(BookingUidGuard)` 改為 `@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 未使用的 import BookingRepository</summary>

新增了 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`，但在檔案中並未使用。這可能是誤加的 import，會觸發 lint 警告。

**建議**：移除此未使用的 import。

**判斷依據**：diff 中新增此 import，但檔案內容未見使用 BookingRepository。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6045 (cache hit 6016) ｜ completion tokens 1282 ｜ PR #16</sub>