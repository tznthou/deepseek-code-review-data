<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要為錄音與逐字稿端點加上正式驗證（Pbac、ApiAuthGuard），並移除過渡期的 message 欄位，同時補上對應的 e2e 測試。整體方向正確，但錄音端點的權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度授權，且 getRecordings 呼叫移除了 await，若該方法為非同步將導致回傳 Promise 而非實際資料。建議修正上述兩點後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，可能回傳 Promise 而非資料 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權 | 0.80 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6` | 新增未使用的 import BookingRepository | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，可能回傳 Promise 而非資料</summary>

在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫被移除了 `await`。若 `getRecordings` 是非同步方法（從測試中 `jest.spyOn(calVideoService, "getRecordings").mockResolvedValue([])` 可推測其回傳 Promise），則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這將導致 API 回傳錯誤的資料型態，前端可能無法正確解析。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件（序列化後可能變成空物件或拋出錯誤），而非錄音列表。

**建議修法**：恢復 `await`，確保取得實際資料：
```ts
const recordings = await this.calVideoService.getRecordings(bookingUid);
```

**判斷依據**：diff 中此行從 `const recordings = await this.calVideoService.getRecordings(bookingUid);` 改為 `const recordings = this.calVideoService.getRecordings(bookingUid);`，移除了 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權</summary>

錄音端點（GET /:bookingUid/recordings）的 `@Permissions` 從 `BOOKING_READ` 改為 `BOOKING_WRITE`。讀取錄音應僅需讀取權限，改為寫入權限可能導致只有具備寫入權限的角色才能存取，或意外允許具有寫入權限但無讀取權限的角色存取。

**失敗情境**：一個僅被授予讀取權限的 API key 將無法存取錄音，而一個僅有寫入權限的 key 卻能讀取錄音，這可能違反最小權限原則。

**建議修法**：若此端點僅供讀取，應維持 `BOOKING_READ`；若確實需要寫入權限，請在 PR 描述中說明原因。

**判斷依據**：diff 中此行從 `@Permissions([BOOKING_READ])` 改為 `@Permissions([BOOKING_WRITE])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6</code> 新增未使用的 import BookingRepository</summary>

此檔案新增了 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`，但在檔案中並未使用。這可能是誤加的 import，會造成 lint 警告或增加不必要的相依性。

**建議修法**：移除此 import。

**判斷依據**：diff 中新增了此 import，但檔案內容沒有使用到 BookingRepository。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4596 (cache hit 4480) ｜ completion tokens 1054 ｜ PR #16</sub>