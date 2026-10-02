<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要為 bookings 的 recordings 與 transcripts 端點加上正式驗證（Pbac、ApiAuthGuard），移除過渡期的 message 欄位，並補上對應的 e2e 測試。整體方向正確，但有一個權限設定錯誤：recordings 端點使用 BOOKING_WRITE 而非 BOOKING_READ，可能導致僅有讀取權限的用戶無法存取錄音，且與 transcripts 端點不一致。此外，getRecordings 呼叫移除了 await，若該方法回傳 Promise 將造成型別不符或未處理的錯誤。建議修正權限並確認 getRecordings 的同步性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | recordings 端點權限誤用 BOOKING_WRITE，應為 BOOKING_READ | 0.95 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，可能導致型別不符或未處理的 Promise | 0.80 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 未使用的 import BookingRepository | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> recordings 端點權限誤用 BOOKING_WRITE，應為 BOOKING_READ</summary>

此端點用於取得錄音，屬於讀取操作，但 `@Permissions` 設為 `BOOKING_WRITE`。這會導致僅有讀取權限的用戶（例如被邀請的參與者）無法存取錄音，且與 transcripts 端點使用 `BOOKING_READ` 不一致。建議改為 `BOOKING_READ`。

**判斷依據**：diff 中將原本的 `@Permissions([BOOKING_READ])` 改為 `@Permissions([BOOKING_WRITE])`，而 transcripts 端點仍使用 `BOOKING_READ`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，可能導致型別不符或未處理的 Promise</summary>

原本 `await this.calVideoService.getRecordings(bookingUid)` 改為 `this.calVideoService.getRecordings(bookingUid)`，若該方法回傳 Promise，則 `recordings` 會是 Promise 而非實際資料，可能導致回傳給客戶端的資料不正確，或未處理的 rejection。請確認 `getRecordings` 是否為同步方法；若非同步，應保留 `await`。

**判斷依據**：diff 中移除了 `await`，但 transcripts 端點仍使用 `await this.calVideoService.getTranscripts(bookingUid)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 未使用的 import BookingRepository</summary>

新增的 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";` 在此檔案中未使用，可能造成 lint 警告。建議移除。

**判斷依據**：diff 新增此 import，但檔案中未見使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6004 (cache hit 4608) ｜ completion tokens 828 ｜ PR #16</sub>