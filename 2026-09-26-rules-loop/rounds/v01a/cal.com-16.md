<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要為錄音與逐字稿端點加上正式的身分驗證與權限控制，並補上對應的 e2e 測試。整體方向正確，但錄音端點的權限從 BOOKING_READ 提升為 BOOKING_WRITE，可能造成僅有讀取權限的整合無法存取錄音，需確認是否為預期行為。此外，getRecordings 的呼叫移除了 await，若該方法為非同步，將導致回傳 Promise 而非實際資料，造成 API 回應錯誤。建議修正 await 並確認權限變更的合理性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，導致回傳 Promise 而非資料 | 0.95 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄音端點權限從 BOOKING_READ 提升為 BOOKING_WRITE，可能破壞現有整合 | 0.80 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 未使用的 import BookingRepository | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，導致回傳 Promise 而非資料</summary>

在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫移除了 `await`。若 `getRecordings` 是非同步方法（從先前程式碼與測試中的 mock 可推斷），則 `recordings` 會是 Promise 物件，而非實際的錄音資料。這將導致 API 回應的 `data` 欄位變成 Promise，序列化後可能變成空物件或錯誤。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 不會是錄音陣列，而是 Promise 的 JSON 表示（通常為 `{}`），造成資料遺失。

**建議修法**：恢復 `await`，改為 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

**判斷依據**：diff 中此行由 `const recordings = await this.calVideoService.getRecordings(bookingUid);` 改為 `const recordings = this.calVideoService.getRecordings(bookingUid);`，移除了 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄音端點權限從 BOOKING_READ 提升為 BOOKING_WRITE，可能破壞現有整合</summary>

`getBookingRecordings` 端點的 `@Permissions` 從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這表示僅具有讀取權限的 API 金鑰或使用者將無法存取錄音，可能導致現有整合失效。

**失敗情境**：一個僅被授予 `BOOKING_READ` 權限的 API 金鑰，原本可以讀取錄音，升級後將收到 403 Forbidden。

**建議修法**：確認此權限變更是否為預期行為。若錄音屬於讀取操作，應維持 `BOOKING_READ`；若確實需要寫入權限，請在 PR 描述中說明原因並通知受影響的使用者。

**判斷依據**：diff 中此行由 `@Permissions([BOOKING_READ])` 改為 `@Permissions([BOOKING_WRITE])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 未使用的 import BookingRepository</summary>

新增了 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`，但在檔案中並未使用。這可能違反 lint 規則（如 no-unused-vars），且增加不必要的相依性。

**建議修法**：移除此 import。

**判斷依據**：diff 中新增此 import，但後續程式碼未使用 BookingRepository。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6035 (cache hit 4480) ｜ completion tokens 1030 ｜ PR #16</sub>