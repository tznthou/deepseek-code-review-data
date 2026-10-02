<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為錄音與逐字稿端點加上正式驗證（Pbac、ApiAuthGuard），移除過渡期訊息，並補上對應的 e2e 測試。整體方向正確，但錄音端點的權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度授權，且 transcripts 端點的 guard 順序可能導致 Pbac 檢查被跳過。此外，get-booking-recordings.output.ts 中新增了一個未使用的 import，需要清理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度授權 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238` | transcripts 端點 guard 順序可能導致 Pbac 檢查被跳過 | 0.70 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 新增未使用的 import | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度授權</summary>

此端點為讀取錄音，但權限從 BOOKING_READ 改為 BOOKING_WRITE。若 BOOKING_WRITE 權限包含修改能力，則擁有寫入權限但無讀取權限的使用者將可存取錄音，可能違反最小權限原則。建議確認 BOOKING_WRITE 的定義，若僅為讀取用途應維持 BOOKING_READ。

**判斷依據**：diff 中將原本的 @Permissions([BOOKING_READ]) 改為 @Permissions([BOOKING_WRITE])，但端點仍為 GET 且回傳錄音資料。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238</code> transcripts 端點 guard 順序可能導致 Pbac 檢查被跳過</summary>

原本的 guard 順序為 BookingUidGuard，現在改為 BookingPbacGuard, ApiAuthGuard, BookingUidGuard。若 BookingPbacGuard 依賴 ApiAuthGuard 設定的使用者資訊，則可能在使用者未通過驗證時就執行 Pbac 檢查，導致錯誤或安全漏洞。建議確認 guard 執行順序與相依性，必要時調整為 ApiAuthGuard 在前。

**判斷依據**：diff 中將 @UseGuards(BookingUidGuard) 改為 @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)，但未提供 guard 內部實作，無法確認順序是否正確。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 新增未使用的 import</summary>

新增了 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`，但在此檔案中並未使用該型別。這會觸發 lint 警告（未使用的 import），建議移除。

**判斷依據**：diff 中新增此 import，但檔案內容未見使用 BookingRepository。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5220 (cache hit 4480) ｜ completion tokens 835 ｜ PR #16</sub>