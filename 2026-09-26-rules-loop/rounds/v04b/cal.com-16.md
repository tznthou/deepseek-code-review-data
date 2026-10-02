<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要為錄音與逐字稿端點加上正式驗證（Pbac、ApiAuthGuard），移除過渡期訊息，並補上對應的 e2e 測試。整體方向正確，但錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度限制，且 getRecordings 呼叫缺少 await 可能導致回傳 Promise 而非實際資料。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，回傳型別不符 | 0.95 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度限制 | 0.80 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 未使用的 import：BookingRepository | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，回傳型別不符</summary>

`this.calVideoService.getRecordings(bookingUid)` 回傳的是 Promise，但此處未使用 `await`，導致 `recordings` 變數型別為 Promise，而非實際的錄音資料陣列。這會使 API 回傳的 `data` 欄位變成 Promise 物件，序列化後可能變成空物件或錯誤內容。

**失敗情境**：當客戶端呼叫此端點時，會收到 `data: {}` 或非預期的序列化結果，造成功能失效。

**建議**：加上 `await`，改為 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

**判斷依據**：diff 中此行由原本的 `await this.calVideoService.getRecordings(bookingUid)` 改為 `this.calVideoService.getRecordings(bookingUid)`，移除了 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度限制</summary>

此端點為讀取錄音，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這可能導致僅有讀取權限的用戶無法存取錄音，違反最小權限原則。

**失敗情境**：具有 `BOOKING_READ` 權限但無 `BOOKING_WRITE` 權限的 API key 或使用者，將無法取得錄音，即使他們有權查看該預約。

**建議**：確認此變更是否為預期。若錄音讀取應與預約讀取權限一致，應保留 `BOOKING_READ`；若確實需要寫入權限，請在 PR 描述中說明原因。

**判斷依據**：diff 中 `@Permissions([BOOKING_READ])` 被改為 `@Permissions([BOOKING_WRITE])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 未使用的 import：BookingRepository</summary>

新增了 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`，但在檔案中並未使用。這可能是誤加，會觸發 lint 警告。

**建議**：移除此未使用的 import。

**判斷依據**：diff 中新增此 import，但檔案內容未見使用該型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5220 (cache hit 5120) ｜ completion tokens 939 ｜ PR #16</sub>