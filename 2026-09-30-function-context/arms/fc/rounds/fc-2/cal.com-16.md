<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將錄製與逐字稿端點從未受保護改為需要驗證與授權，並新增對應的 e2e 測試。主要風險在於錄製端點的權限從 BOOKING_READ 改為 BOOKING_WRITE，可能造成授權過嚴或過鬆；此外，getRecordings 呼叫移除了 await，若該方法回傳 Promise 將導致資料型別錯誤。整體方向正確，但需確認權限變更的意圖與非同步處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:171` | 錄製端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能造成授權不當 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，可能回傳 Promise 而非實際資料 | 0.70 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 新增未使用的 BookingRepository 型別匯入 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:171</code> 錄製端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能造成授權不當</summary>

此端點為讀取操作，但權限從 BOOKING_READ 改為 BOOKING_WRITE。若 BOOKING_WRITE 權限比 BOOKING_READ 更嚴格，可能導致原本可讀取的使用者失去存取權；反之，若 BOOKING_WRITE 權限較寬鬆，則可能允許未授權使用者讀取錄製內容。請確認此變更的意圖，並確保權限設定符合最小權限原則。

**判斷依據**：diff 中將 @Permissions([BOOKING_READ]) 改為 @Permissions([BOOKING_WRITE])，但端點仍為 GET 且描述為讀取錄製內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，可能回傳 Promise 而非實際資料</summary>

原本 `await this.calVideoService.getRecordings(bookingUid)` 改為 `this.calVideoService.getRecordings(bookingUid)`，若該方法回傳 Promise，則 `recordings` 會是 Promise 物件，導致回傳給客戶端的資料不正確。請確認 `getRecordings` 的實作是否為同步，否則應保留 await。

**判斷依據**：diff 中移除了 await，但其他類似呼叫（如 getTranscripts）仍保留 await。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 新增未使用的 BookingRepository 型別匯入</summary>

此匯入似乎未被使用，可能造成 lint 錯誤或混淆。請確認是否真的需要，否則應移除。

**判斷依據**：diff 中新增此匯入，但檔案中未見使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11307 (cache hit 11264) ｜ completion tokens 787 ｜ PR #16</sub>