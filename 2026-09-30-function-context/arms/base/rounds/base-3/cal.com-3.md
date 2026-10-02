<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程中的 Prisma 直接呼叫改為依賴注入的 repository，並新增對應的介面與實作。主要風險在於 UserRepository 的 userSelect 移除了 locale 欄位，可能導致取消流程中取得 organizer 時缺少 locale，進而影響翻譯或時區處理。此外，部分 repository 的介面定義不完整，且新增的測試僅驗證成功結果，未涵蓋資料庫狀態或錯誤情境。建議先確認 locale 移除的影響，並補齊介面與測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/users/repositories/UserRepository.ts:100` | 移除 userSelect 中的 locale 可能導致取消流程缺少 locale | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 取消單一預約時改用 uid 作為唯一條件，可能忽略 id 參數 | 0.75 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:513` | 大量取消 recurring bookings 時，查詢條件從 `gte: new Date()` 改為 `gte: bookingToDelete.startTime` | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1509` | 新增的 `update` 方法回傳型別可能與介面不符 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:147` | 依賴注入的 fallback 實例化可能導致不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/users/repositories/UserRepository.ts:100</code> 移除 userSelect 中的 locale 可能導致取消流程缺少 locale</summary>

在 `userSelect` 中移除了 `locale: true`，但取消流程中 `handler` 會使用 `organizer.locale` 來取得翻譯：`const tOrganizer = await getTranslation(organizer.locale ?? "en", "common");`。若 `UserRepository.findByIdOrThrow` 使用此 `userSelect`，則回傳的 organizer 物件將沒有 `locale` 屬性，導致 `organizer.locale` 為 `undefined`，最終 fallback 到 `"en"`，可能造成非英語使用者的通知或錯誤訊息語言不正確。建議確認 `findByIdOrThrow` 是否使用此 `userSelect`，若需要 locale 則應保留，或改用其他方式取得。

**判斷依據**：diff 中 `packages/features/users/repositories/UserRepository.ts` 的 `userSelect` 移除了 `locale: true`，而 `handleCancelBooking.ts` 中使用了 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 取消單一預約時改用 uid 作為唯一條件，可能忽略 id 參數</summary>

原本的程式碼使用 `const where: Prisma.BookingWhereUniqueInput = uid ? { uid } : { id };`，會根據是否有 `uid` 來決定用哪個唯一鍵。修改後直接使用 `where: { uid: bookingToDelete.uid }`，完全忽略傳入的 `id`。如果呼叫端只提供 `id` 而沒有 `uid`，或 `uid` 與 `id` 不一致，可能導致更新錯誤的預約或找不到預約。建議保留原本的條件邏輯，或確保 `bookingToDelete.uid` 一定存在且正確。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的 `else` 分支，原本的 `where` 條件被改為固定使用 `uid`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:513</code> 大量取消 recurring bookings 時，查詢條件從 `gte: new Date()` 改為 `gte: bookingToDelete.startTime`</summary>

原本的 `findMany` 查詢使用 `startTime: { gte: new Date() }`，會找出所有未來時間的 recurring bookings。修改後改為 `gte: bookingToDelete.startTime`，這會包含過去已發生的 bookings（如果 `bookingToDelete.startTime` 在過去）。這可能導致取消不該取消的過去 bookings，或影響後續的處理邏輯。請確認此變更是否符合預期，特別是在處理過去 recurring events 時。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的 `findManyIncludeWorkflowRemindersAndReferences` 呼叫，原本的 `gte: new Date()` 被改為 `gte: bookingToDelete.startTime`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> 新增的 `update` 方法回傳型別可能與介面不符</summary>

`IBookingRepository` 介面中定義 `update` 回傳 `Promise<Booking>`，但 `BookingRepository` 的 `update` 方法直接回傳 `this.prismaClient.booking.update(...)`，其回傳型別是 Prisma 的 `Booking` 型別，可能包含更多欄位，但型別上應相容。然而，若 `BookingUpdateData` 的欄位與 Prisma 的 `BookingUpdateInput` 不完全一致，可能導致型別錯誤。建議確認介面與實作的型別一致性。

**判斷依據**：diff 中 `BookingRepository.ts` 新增的 `update` 方法，以及 `IBookingRepository.ts` 中的介面定義。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:147</code> 依賴注入的 fallback 實例化可能導致不一致</summary>

在 `handler` 中，若未提供 `dependencies`，會使用 `new UserRepository(prismaClient)` 等建立實例。但 `UserRepository` 的建構子可能預期不同的參數（例如需要其他依賴），且 `ProfileRepository` 的建構子接受 `{ prismaClient }` 物件，而 `BookingReferenceRepository` 也接受 `{ prismaClient }`。這些 fallback 實例化可能與實際 DI 容器提供的實例不同，導致行為不一致。建議統一依賴的建立方式，或確保 fallback 與 DI 使用相同的建構參數。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的 `handler` 函式內的 fallback 實例化。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14899 (cache hit 14848) ｜ completion tokens 1719 ｜ PR #3</sub>