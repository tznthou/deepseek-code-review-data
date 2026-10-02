<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為錄影與逐字稿端點加上正式驗證（ApiAuthGuard、BookingPbacGuard），並將錄影端點的權限從 BOOKING_READ 改為 BOOKING_WRITE，同時移除過渡期的 message 欄位與相關測試。主要風險在於錄影端點權限提升可能造成向後不相容，且未移除的未使用 import 顯示清理不完整。整體而言，變更方向合理，但需確認權限變更的影響與測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄影端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能造成向後不相容 | 0.80 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 未使用的 import：BookingRepository | 0.90 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | 移除 await 可能導致未處理的 Promise rejection | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄影端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能造成向後不相容</summary>

原本的 `@Permissions([BOOKING_READ])` 被改為 `@Permissions([BOOKING_WRITE])`。這表示原本具有讀取權限的 API 金鑰或使用者將無法再存取錄影，可能導致現有整合失效。若此變更非刻意為之，應改回 `BOOKING_READ`；若為刻意，則需在文件中明確標示 breaking change，並確認所有相關測試已更新。

**判斷依據**：diff 中將 `@Permissions([BOOKING_READ])` 改為 `@Permissions([BOOKING_WRITE])`，而 transcripts 端點仍維持 `BOOKING_READ`，顯示兩者權限不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 未使用的 import：BookingRepository</summary>

新增的 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";` 在此檔案中並未被使用。這可能是誤加的 import，應移除，以避免 lint 警告（R06）並保持程式碼整潔。

**判斷依據**：diff 中新增此 import，但檔案內容未使用 BookingRepository。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> 移除 await 可能導致未處理的 Promise rejection</summary>

`getBookingRecordings` 方法中，原本 `await this.calVideoService.getRecordings(bookingUid)` 改為 `this.calVideoService.getRecordings(bookingUid)`，移除了 `await`。若 `getRecordings` 回傳 Promise 且可能 reject，則錯誤將不會被此 async 方法捕獲，可能導致未處理的 rejection。建議保留 `await` 以確保錯誤能被正確處理。

**判斷依據**：diff 中將 `await this.calVideoService.getRecordings(bookingUid)` 改為 `this.calVideoService.getRecordings(bookingUid)`，且方法仍為 async。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6035 (cache hit 1536) ｜ completion tokens 850 ｜ PR #16</sub>