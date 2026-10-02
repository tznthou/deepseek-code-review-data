<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程中的 Prisma 直接呼叫改為透過 repository 注入，並新增對應的 repository 類別與 DI 模組。主要風險在於 UserRepository 的 userSelect 移除了 locale 欄位，可能導致取消流程中取得 organizer 時缺少 locale，進而影響翻譯或時區處理。此外，部分 repository 介面定義不完整，且新增的測試僅驗證成功結果，未涵蓋資料庫狀態驗證。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位可能導致取消流程缺少必要資料 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:513` | 取消後續預約時查詢條件可能遺漏時區或邊界處理 | 0.75 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 取消單一預約時改用 uid 作為唯一條件可能忽略 id 參數 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | 新增的 updateMany 方法未回傳更新筆數，可能影響錯誤處理 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法缺少 await 回傳，可能導致未處理的 Promise | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未遵循介面定義，可能導致型別錯誤 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未回傳更新筆數，可能影響錯誤處理 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未回傳更新筆數，可能影響錯誤處理 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未回傳更新筆數，可能影響錯誤處理 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未回傳更新筆數，可能影響錯誤處理 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位可能導致取消流程缺少必要資料</summary>

在 `userSelect` 中移除了 `locale: true`，但取消流程中 `handler` 會使用 `organizer.locale` 來取得翻譯（`getTranslation(organizer.locale ?? "en", "common")`）。若 `UserRepository.findByIdOrThrow` 使用此 `userSelect`，則回傳的 organizer 物件將缺少 `locale` 屬性，導致翻譯回退為英文，可能影響使用者體驗。

建議：確認 `findByIdOrThrow` 是否使用此 `userSelect`，若需要 locale，應保留該欄位或改用其他方式取得。

**判斷依據**：diff 中移除了 `locale: true`，而 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:513</code> 取消後續預約時查詢條件可能遺漏時區或邊界處理</summary>

在取消後續預約的邏輯中，原本的 `findMany` 使用 `gte: new Date()`，但改為 `gte: bookingToDelete.startTime`。這可能導致若 `bookingToDelete.startTime` 早於現在，則會包含已過去的預約；若晚於現在，則可能遺漏部分應取消的預約。需確認此變更是否符合預期。

建議：確認 `bookingToDelete.startTime` 的語意，並考慮是否應使用 `new Date()` 或明確的邊界條件。

**判斷依據**：diff 中將 `gte: new Date()` 改為 `gte: bookingToDelete.startTime`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 取消單一預約時改用 uid 作為唯一條件可能忽略 id 參數</summary>

原本的 `where` 條件會根據 `uid` 或 `id` 擇一使用，但改為固定使用 `uid: bookingToDelete.uid`。若呼叫端僅提供 `id` 而未提供 `uid`，則可能導致查詢失敗或更新錯誤的預約。

建議：確認 `bookingToDelete.uid` 是否總是存在，或保留原本的條件邏輯。

**判斷依據**：diff 中移除了原本的 `const where: Prisma.BookingWhereUniqueInput = uid ? { uid } : { id };` 並改為固定使用 `uid`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> 新增的 updateMany 方法未回傳更新筆數，可能影響錯誤處理</summary>

`updateMany` 方法未回傳 `{ count: number }`，但介面 `IBookingRepository` 定義的回傳型別為 `Promise<{ count: number }>`。這可能導致呼叫端無法確認更新是否成功，或型別不一致。

建議：讓 `updateMany` 回傳 `this.prismaClient.booking.updateMany` 的結果，或調整介面定義。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳值，但介面定義要求回傳 `{ count: number }`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法缺少 await 回傳，可能導致未處理的 Promise</summary>

`updateMany` 方法中使用了 `await`，但未將結果回傳，且方法本身未標記為 `async`？實際上已標記為 `async`，但未回傳值。這可能導致呼叫端無法正確等待操作完成或取得結果。

建議：回傳 `this.prismaClient.booking.updateMany` 的結果。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未遵循介面定義，可能導致型別錯誤</summary>

介面 `IBookingRepository` 定義 `updateMany` 回傳 `Promise<{ count: number }>`，但實作未回傳任何值。這會造成型別不符，可能導致編譯錯誤或執行時期問題。

建議：修正實作以符合介面。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳值，但介面定義要求回傳 `{ count: number }`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未回傳更新筆數，可能影響錯誤處理</summary>

`updateMany` 方法未回傳 `{ count: number }`，但介面 `IBookingRepository` 定義的回傳型別為 `Promise<{ count: number }>`。這可能導致呼叫端無法確認更新是否成功，或型別不一致。

建議：讓 `updateMany` 回傳 `this.prismaClient.booking.updateMany` 的結果，或調整介面定義。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳值，但介面定義要求回傳 `{ count: number }`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未回傳更新筆數，可能影響錯誤處理</summary>

`updateMany` 方法未回傳 `{ count: number }`，但介面 `IBookingRepository` 定義的回傳型別為 `Promise<{ count: number }>`。這可能導致呼叫端無法確認更新是否成功，或型別不一致。

建議：讓 `updateMany` 回傳 `this.prismaClient.booking.updateMany` 的結果，或調整介面定義。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳值，但介面定義要求回傳 `{ count: number }`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未回傳更新筆數，可能影響錯誤處理</summary>

`updateMany` 方法未回傳 `{ count: number }`，但介面 `IBookingRepository` 定義的回傳型別為 `Promise<{ count: number }>`。這可能導致呼叫端無法確認更新是否成功，或型別不一致。

建議：讓 `updateMany` 回傳 `this.prismaClient.booking.updateMany` 的結果，或調整介面定義。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳值，但介面定義要求回傳 `{ count: number }`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未回傳更新筆數，可能影響錯誤處理</summary>

`updateMany` 方法未回傳 `{ count: number }`，但介面 `IBookingRepository` 定義的回傳型別為 `Promise<{ count: number }>`。這可能導致呼叫端無法確認更新是否成功，或型別不一致。

建議：讓 `updateMany` 回傳 `this.prismaClient.booking.updateMany` 的結果，或調整介面定義。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳值，但介面定義要求回傳 `{ count: number }`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16307 (cache hit 14848) ｜ completion tokens 2822 ｜ PR #3</sub>