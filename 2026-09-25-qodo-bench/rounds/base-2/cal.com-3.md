<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預約流程中的 Prisma 直接呼叫重構為依賴注入的 repository，並新增了對應的測試。整體方向正確，但存在幾個需要修正的問題：最嚴重的是 `BookingRepository.update` 方法缺少 `select`，導致回傳的 `updatedBooking` 缺少 `references` 與 `workflowReminders` 欄位，後續程式碼存取時會出錯；此外，`UserRepository` 的 `userSelect` 移除了 `locale` 欄位，但取消流程中仍使用 `organizer.locale`，可能造成執行時錯誤。另有介面型別定義不完整、測試未驗證資料庫狀態等次要問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/repositories/BookingRepository.ts:1509` | `update` 方法缺少 `select`，回傳物件缺少 `references` 與 `workflowReminders` | 0.95 |
| 🛑 | Blocker | `packages/features/users/repositories/UserRepository.ts:98` | 移除 `locale` 欄位導致取消流程中 `organizer.locale` 可能為 undefined | 0.90 |
| ⚠️ | Major | `packages/lib/server/repository/dto/IBookingRepository.ts:46` | `IBookingRepository` 介面缺少 `updateIncludeWorkflowRemindersAndReferences` 方法 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1057` | 新增測試未驗證資料庫狀態，僅檢查回傳值 | 0.75 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:497` | `gte` 條件從 `new Date()` 改為 `bookingToDelete.startTime` 可能改變行為 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | `updateMany` 方法缺少回傳值 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:147` | 依賴注入 fallback 使用全域 `prisma` 可能造成測試隔離問題 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> `update` 方法缺少 `select`，回傳物件缺少 `references` 與 `workflowReminders`</summary>

在 `handleCancelBooking.ts` 中，`bookingRepository.updateIncludeWorkflowRemindersAndReferences` 被呼叫後，回傳值被 push 到 `updatedBookings`，後續程式碼會存取 `updatedBooking.references` 與 `updatedBooking.workflowReminders`。但 `BookingRepository.update` 方法（第 1512 行）沒有指定 `select`，因此回傳的 `Booking` 物件不會包含這兩個關聯欄位，導致執行時錯誤。

建議在 `update` 方法中加入與 `updateIncludeWorkflowRemindersAndReferences` 相同的 `select`，或直接改用 `updateIncludeWorkflowRemindersAndReferences`。

**判斷依據**：diff 中 `handleCancelBooking.ts` 將原本的 `prisma.booking.update` 改為 `bookingRepository.updateIncludeWorkflowRemindersAndReferences`，但 `BookingRepository.update` 方法沒有 select，回傳型別為 `Booking`，不包含 `references` 與 `workflowReminders`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 `locale` 欄位導致取消流程中 `organizer.locale` 可能為 undefined</summary>

`UserRepository` 的 `userSelect` 移除了 `locale` 欄位，但 `handleCancelBooking.ts` 中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`）。若 `findByIdOrThrow` 使用此 select，回傳的 organizer 將沒有 `locale` 屬性，可能導致執行時錯誤或 fallback 行為不如預期。

請確認 `findByIdOrThrow` 是否使用此 select，並考慮保留 `locale` 欄位或調整取消流程的處理。

**判斷依據**：diff 中 `UserRepository.ts` 刪除了 `locale: true`，而 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/server/repository/dto/IBookingRepository.ts:46</code> `IBookingRepository` 介面缺少 `updateIncludeWorkflowRemindersAndReferences` 方法</summary>

`BookingRepository` 實作了 `IBookingRepository`，但介面中未宣告 `updateIncludeWorkflowRemindersAndReferences` 方法。這可能導致型別檢查不一致，且未來其他實作可能遺漏此方法。

建議在介面中加入此方法的簽章。

**判斷依據**：diff 中 `BookingRepository` 新增了 `updateIncludeWorkflowRemindersAndReferences` 方法，但 `IBookingRepository` 介面未包含此方法。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1057</code> 新增測試未驗證資料庫狀態，僅檢查回傳值</summary>

新增的四個測試僅驗證 `result.success`、`result.onlyRemovedAttendee` 和 `result.bookingId`，未驗證資料庫中的實際變更（例如 attendees 是否被刪除、booking status 是否更新、booking references 是否被標記為 deleted）。這可能讓測試無法捕捉到 repository 實作中的錯誤。

建議加入對資料庫狀態的斷言，例如使用 Prisma 查詢確認。

**判斷依據**：diff 中新增的測試僅有這些斷言，未查詢資料庫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:497</code> `gte` 條件從 `new Date()` 改為 `bookingToDelete.startTime` 可能改變行為</summary>

在取消後續 recurring bookings 時，原本的 `gte: new Date()` 被改為 `gte: bookingToDelete.startTime`。這可能導致取消的 bookings 集合不同：如果 `bookingToDelete.startTime` 早於目前時間，會包含過去已發生的 bookings；如果晚於目前時間，則可能遺漏應取消的 bookings。

請確認此變更是否符合預期，並考慮是否應保留原本的 `new Date()` 或使用其他條件。

**判斷依據**：diff 中 `handleCancelBooking.ts` 將 `gte: new Date()` 改為 `gte: bookingToDelete.startTime`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> `updateMany` 方法缺少回傳值</summary>

`updateMany` 方法沒有回傳 `count`，但介面 `IBookingRepository` 定義回傳 `Promise<{ count: number }>`。雖然目前呼叫端未使用回傳值，但型別不一致可能導致未來誤用。

建議回傳 `this.prismaClient.booking.updateMany` 的結果。

**判斷依據**：diff 中 `updateMany` 方法未回傳值，但介面定義回傳 `Promise<{ count: number }>`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:147</code> 依賴注入 fallback 使用全域 `prisma` 可能造成測試隔離問題</summary>

當 `dependencies` 未提供時，handler 會使用全域 `prisma` 建立 repositories。這在測試中可能導致測試之間共享狀態，且難以 mock。建議在測試中一律注入 dependencies，或提供明確的測試用 prisma client。

**判斷依據**：diff 中 handler 的 fallback 使用全域 `prisma`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14899 (cache hit 14848) ｜ completion tokens 2177 ｜ PR #3</sub>