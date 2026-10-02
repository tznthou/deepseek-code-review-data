<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要為錄音與逐字稿端點加上正式驗證（Pbac、ApiAuthGuard），並移除過渡期的 message 欄位，同時補上對應的 e2e 測試。整體方向正確，但錄音端點的權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度授權，且 getRecordings 呼叫少了 await，可能造成回傳 Promise 而非實際資料。建議修正這兩個問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料 | 0.95 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238` | 逐字稿端點的 guard 順序可能影響錯誤回應 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料</summary>

在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

**判斷依據**：diff 中此行由原本的 `await this.calVideoService.getRecordings(bookingUid)` 改為沒有 `await` 的版本。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權</summary>

此端點是讀取錄音資料，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這代表只有具備寫入權限的 API key 才能存取錄音，而原本具有讀取權限的 key 將無法使用。這可能破壞向後相容性，且不符合最小權限原則。

**失敗情境**：使用僅有 `BOOKING_READ` 權限的 API key 呼叫此端點會得到 403，但預期應該允許讀取。

**建議修正**：維持 `BOOKING_READ` 權限，除非有明確理由需要寫入權限。

**判斷依據**：diff 中此行由 `@Permissions([BOOKING_READ])` 改為 `@Permissions([BOOKING_WRITE])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238</code> 逐字稿端點的 guard 順序可能影響錯誤回應</summary>

在 `getBookingTranscripts` 端點，guard 順序從原本的 `BookingUidGuard` 改為 `BookingPbacGuard, ApiAuthGuard, BookingUidGuard`。若 `BookingPbacGuard` 在 `ApiAuthGuard` 之前執行，未驗證的請求可能會先被 Pbac 拒絕，導致回應 403 而非 401。這可能影響 API 的語意一致性。

**失敗情境**：未帶 token 的請求可能收到 403 而非預期的 401。

**建議修正**：確認 guard 執行順序是否符合預期，通常 `ApiAuthGuard` 應在最前面以正確回傳 401。

**判斷依據**：diff 中此行由 `@UseGuards(BookingUidGuard)` 改為 `@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4596 (cache hit 1536) ｜ completion tokens 1034 ｜ PR #16</sub>