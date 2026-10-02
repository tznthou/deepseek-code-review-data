<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預約流程中的 Prisma 直接呼叫改為依賴注入的 repository，並新增了對應的介面與實作。主要風險在於 `BookingRepository.updateMany` 的實作未回傳 `{ count }`，與介面定義不符，可能導致呼叫端誤判；另外 `UserRepository` 的 `userSelect` 移除了 `locale` 欄位，但取消流程中仍使用 `organizer.locale`，可能造成執行時錯誤。建議先修正這兩個問題再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 未回傳 { count }，與介面不符 | 0.95 |
| 🛑 | Blocker | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位可能導致取消流程錯誤 | 0.90 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:500` | updateMany 呼叫未處理回傳值，可能掩蓋錯誤 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:513` | findManyIncludeWorkflowRemindersAndReferences 的 where 條件可能遺漏時區處理 | 0.75 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:546` | updateIncludeWorkflowRemindersAndReferences 的 where 條件改為 uid 可能影響行為 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1509` | update 方法未使用 select，可能回傳過多資料 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1549` | findManyIncludeWorkflowRemindersAndReferences 未限制回傳筆數 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 未回傳 { count }，與介面不符</summary>

`BookingRepository.updateMany` 的實作呼叫 `this.prismaClient.booking.updateMany` 後沒有回傳結果，但介面 `IBookingRepository` 定義此方法應回傳 `Promise<{ count: number }>`。這會導致呼叫端（例如 `handleCancelBooking` 中的 `await bookingRepository.updateMany(...)`）取得 `undefined`，若後續程式碼依賴回傳值（例如檢查更新筆數）將發生錯誤。

建議：在實作中回傳 `await this.prismaClient.booking.updateMany(...)` 的結果，或調整介面定義。

**判斷依據**：diff 中新增的 `updateMany` 方法（行 1502-1508）缺少 return，而 `IBookingRepository` 介面（packages/lib/server/repository/dto/IBookingRepository.ts）定義回傳 `Promise<{ count: number }>`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位可能導致取消流程錯誤</summary>

`UserRepository` 的 `userSelect` 移除了 `locale` 欄位，但在 `handleCancelBooking` 中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`）。若 `findByIdOrThrow` 使用此 `userSelect`，回傳的 organizer 物件將缺少 `locale`，導致 `organizer.locale` 為 `undefined`，可能觸發錯誤或使用錯誤的預設語言。

建議：確認 `findByIdOrThrow` 是否使用此 `userSelect`，若需要 `locale` 則應保留該欄位，或改用其他方式取得。

**判斷依據**：diff 中 `packages/features/users/repositories/UserRepository.ts` 的 `userSelect` 移除了 `locale: true`（行 101 附近），而 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:500</code> updateMany 呼叫未處理回傳值，可能掩蓋錯誤</summary>

在 `handleCancelBooking` 中，`await bookingRepository.updateMany(...)` 的結果未被使用。若 `updateMany` 實作未正確回傳（如前述 blocker），此處不會察覺錯誤。此外，即使回傳 `{ count }`，也應檢查是否更新了預期的筆數，以確保取消操作成功。

建議：檢查回傳的 `count` 是否符合預期，並在不符合時記錄錯誤或拋出例外。

**判斷依據**：diff 中 `handleCancelBooking.ts` 行 497 的 `await bookingRepository.updateMany(...)` 未使用回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:513</code> findManyIncludeWorkflowRemindersAndReferences 的 where 條件可能遺漏時區處理</summary>

在 `handleCancelBooking` 中，`findManyIncludeWorkflowRemindersAndReferences` 的 `where` 條件使用 `gte: bookingToDelete.startTime`，但 `bookingToDelete.startTime` 是 Date 物件，可能包含時區資訊。若資料庫儲存的是 UTC，而此處傳入的 Date 未正確轉換，可能導致查詢結果不正確。

建議：確認 `bookingToDelete.startTime` 的時區處理，必要時使用 UTC 時間進行比較。

**判斷依據**：diff 中 `handleCancelBooking.ts` 行 510 的 `gte: bookingToDelete.startTime` 可能涉及時區問題。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> updateIncludeWorkflowRemindersAndReferences 的 where 條件改為 uid 可能影響行為</summary>

原本的 `prisma.booking.update` 使用 `where: uid ? { uid } : { id }`，現在改為固定使用 `uid: bookingToDelete.uid`。若 `bookingToDelete.uid` 為空或未定義，將導致查詢失敗。雖然 `bookingToDelete` 應有 uid，但此變更可能影響某些邊界情況。

建議：確認 `bookingToDelete.uid` 一定存在，或保留原本的條件邏輯。

**判斷依據**：diff 中 `handleCancelBooking.ts` 行 540 的 where 條件從 `uid ? { uid } : { id }` 改為固定 `{ uid: bookingToDelete.uid }`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> update 方法未使用 select，可能回傳過多資料</summary>

`BookingRepository.update` 方法直接呼叫 `this.prismaClient.booking.update` 而未指定 `select`，可能回傳完整的 Booking 物件，包含不必要的關聯資料，影響效能。若呼叫端只需要部分欄位，建議加入 `select` 參數。

**判斷依據**：diff 中新增的 `update` 方法（行 1510-1515）未指定 select。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1549</code> findManyIncludeWorkflowRemindersAndReferences 未限制回傳筆數</summary>

`findManyIncludeWorkflowRemindersAndReferences` 可能回傳大量資料，若 recurringEventId 對應的 bookings 很多，可能造成記憶體壓力。建議加入分頁或限制筆數，或確認此查詢僅用於取消流程且筆數可控。

**判斷依據**：diff 中新增的 `findManyIncludeWorkflowRemindersAndReferences` 方法（行 1530-1545）未限制回傳筆數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14899 (cache hit 1536) ｜ completion tokens 2148 ｜ PR #3</sub>