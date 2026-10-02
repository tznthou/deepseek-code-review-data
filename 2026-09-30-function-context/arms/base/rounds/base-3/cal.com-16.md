<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要為錄音與逐字稿端點加上正式驗證（Pbac、ApiAuthGuard），並移除過渡期的 message 欄位與相關測試。整體方向正確，但錄音端點的權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度授權，且 getRecordings 呼叫缺少 await 可能導致回傳 Promise 而非實際資料，需要修正。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，可能回傳 Promise 而非實際資料 | 0.95 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權 | 0.80 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 新增的 BookingRepository import 似乎未使用 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，可能回傳 Promise 而非實際資料</summary>

在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。如果 `getRecordings` 是非同步方法，則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這會導致 API 回傳錯誤的資料格式，且可能造成序列化問題。請確認 `getRecordings` 是否為 async，若是則必須加上 `await`。

**判斷依據**：diff 中此行從 `await this.calVideoService.getRecordings(bookingUid)` 改為 `this.calVideoService.getRecordings(bookingUid)`，移除了 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權</summary>

錄音端點原本使用 `@Permissions([BOOKING_READ])`，現在改為 `@Permissions([BOOKING_WRITE])`。讀取錄音應只需要讀取權限，改為寫入權限可能讓具有寫入權限但無讀取權限的使用者也能存取錄音，造成權限擴張。除非有特殊原因，否則應維持 `BOOKING_READ`。

**判斷依據**：diff 中此行從 `@Permissions([BOOKING_READ])` 改為 `@Permissions([BOOKING_WRITE])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 新增的 BookingRepository import 似乎未使用</summary>

在 `get-booking-recordings.output.ts` 中新增了 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`，但在此檔案中沒有看到使用 `BookingRepository` 的地方。這可能是多餘的 import，建議移除以避免 lint 錯誤。

**判斷依據**：diff 中新增此 import，但檔案內容未使用該型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4596 (cache hit 4480) ｜ completion tokens 825 ｜ PR #16</sub>