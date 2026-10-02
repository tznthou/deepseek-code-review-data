<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預約流程中的直接 Prisma 呼叫重構為依賴注入的 repository 類別，並新增對應的 DI 模組與介面。主要風險在於 `BookingCancelService` 的相依性注入設定可能不完整，導致執行時期錯誤；此外，`UserRepository` 的 `userSelect` 移除了 `locale` 欄位，可能影響取消流程中取得翻譯的邏輯。建議優先確認 DI 設定與 `locale` 欄位的影響。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/di/BookingCancelService.module.ts:21` | DI 模組缺少 bookingRepository 的相依性設定 | 0.90 |
| ⚠️ | Major | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位可能影響取消流程的翻譯邏輯 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:517` | 取消後續預約時查詢條件可能不正確 | 0.75 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:540` | 取消單一預約時改用 uid 作為唯一條件可能導致錯誤 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | 新增的 updateMany 方法缺少回傳值 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:1` | 檔案使用單引號，可能違反格式化規範 | 0.50 |
| 🔸 | Minor | `packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:3` | 檔案使用單引號，可能違反格式化規範 | 0.50 |
| 🔸 | Minor | `packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:5` | 檔案使用單引號，可能違反格式化規範 | 0.50 |
| 🔸 | Minor | `packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:8` | 檔案使用單引號，可能違反格式化規範 | 0.50 |
| 🔸 | Minor | `packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:9` | 檔案使用單引號，可能違反格式化規範 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/di/BookingCancelService.module.ts:21</code> DI 模組缺少 bookingRepository 的相依性設定</summary>

在 `BookingCancelService.module.ts` 中，`depsMap` 設定了 `userRepository`、`bookingRepository`、`profileRepository`、`bookingReferenceRepository`、`attendeeRepository`，但 `bookingRepository` 的 module loader 是從 `@calcom/features/di/modules/Booking` 匯入，而該模組可能未正確設定或未提供 `BookingRepository` 的實例。這可能導致執行時期無法解析 `bookingRepository` 依賴，造成服務初始化失敗。

建議確認 `@calcom/features/di/modules/Booking` 是否正確匯出 `BookingRepository` 的 module loader，並確保其相依性（如 Prisma client）已正確設定。

**判斷依據**：diff 中 `BookingCancelService.module.ts` 的 `depsMap` 新增了 `bookingRepository: bookingRepositoryModuleLoader`，但未顯示 `bookingRepositoryModuleLoader` 的來源模組內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位可能影響取消流程的翻譯邏輯</summary>

在 `UserRepository.ts` 中，`userSelect` 移除了 `locale: true`。然而，在 `handleCancelBooking.ts` 中，取消流程會使用 `organizer.locale` 來取得翻譯（`getTranslation(organizer.locale ?? "en", "common")`）。如果 `userRepository.findByIdOrThrow` 回傳的物件不再包含 `locale`，則 `organizer.locale` 將是 `undefined`，導致翻譯回退到英文，可能造成使用者看到的語言不正確。

建議確認 `userRepository.findByIdOrThrow` 的實作是否仍會回傳 `locale`，或是在取消流程中改用其他方式取得使用者的 locale。

**判斷依據**：diff 顯示 `UserRepository.ts` 中 `userSelect` 移除了 `locale: true`，而 `handleCancelBooking.ts` 中使用了 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:517</code> 取消後續預約時查詢條件可能不正確</summary>

在 `handleCancelBooking.ts` 中，原本的 `prisma.booking.findMany` 查詢條件為 `startTime: { gte: new Date() }`，但重構後改為 `startTime: { gte: bookingToDelete.startTime }`。這可能改變行為：原本是取消「現在時間之後」的所有後續預約，現在變成取消「起始時間等於或晚於被取消預約」的所有預約。如果被取消的預約是過去的預約，則會包含過去已發生的預約，可能導致誤取消。

建議確認此變更是否符合預期，或改回使用 `new Date()` 作為基準。

**判斷依據**：diff 顯示 `handleCancelBooking.ts` 中 `findManyIncludeWorkflowRemindersAndReferences` 的 `where` 條件從 `gte: new Date()` 改為 `gte: bookingToDelete.startTime`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:540</code> 取消單一預約時改用 uid 作為唯一條件可能導致錯誤</summary>

在 `handleCancelBooking.ts` 中，原本的 `prisma.booking.update` 使用 `where: uid ? { uid } : { id }`，但重構後改為 `where: { uid: bookingToDelete.uid }`。如果 `bookingToDelete.uid` 為 `undefined` 或空字串，則可能無法正確定位預約，導致更新失敗或更新到錯誤的預約。

建議確認 `bookingToDelete.uid` 在取消流程中一定存在，或保留原本的條件邏輯。

**判斷依據**：diff 顯示 `handleCancelBooking.ts` 中 `updateIncludeWorkflowRemindersAndReferences` 的 `where` 條件改為固定使用 `uid`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> 新增的 updateMany 方法缺少回傳值</summary>

在 `BookingRepository.ts` 中，新增的 `updateMany` 方法沒有回傳值，但介面 `IBookingRepository` 定義了 `updateMany` 應回傳 `Promise<{ count: number }>`。這可能導致型別不符，且呼叫端無法取得更新筆數。

建議讓 `updateMany` 回傳 `this.prismaClient.booking.updateMany` 的結果，以符合介面定義。

**判斷依據**：diff 顯示 `BookingRepository.ts` 新增的 `updateMany` 方法僅 `await` 而無回傳，但 `IBookingRepository` 介面要求回傳 `Promise<{ count: number }>`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:1</code> 檔案使用單引號，可能違反格式化規範</summary>

在 `PrismaBookingAttendeeRepository.ts` 中，import 陳述式使用了單引號（`'@calcom/prisma/client'`），而專案規範 [R03] 要求使用雙引號。這可能導致 lint 或格式化檢查失敗。

建議將單引號改為雙引號。

**判斷依據**：diff 顯示 `PrismaBookingAttendeeRepository.ts` 的 import 使用單引號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:3</code> 檔案使用單引號，可能違反格式化規範</summary>

在 `PrismaBookingAttendeeRepository.ts` 中，import 陳述式使用了單引號（`'../lib/dto/IBookingAttendeeRepository'`），而專案規範 [R03] 要求使用雙引號。這可能導致 lint 或格式化檢查失敗。

建議將單引號改為雙引號。

**判斷依據**：diff 顯示 `PrismaBookingAttendeeRepository.ts` 的 import 使用單引號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:5</code> 檔案使用單引號，可能違反格式化規範</summary>

在 `PrismaBookingAttendeeRepository.ts` 中，類別宣告後的程式碼使用了單引號（`'@calcom/prisma/client'`），而專案規範 [R03] 要求使用雙引號。這可能導致 lint 或格式化檢查失敗。

建議將單引號改為雙引號。

**判斷依據**：diff 顯示 `PrismaBookingAttendeeRepository.ts` 的 import 使用單引號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:8</code> 檔案使用單引號，可能違反格式化規範</summary>

在 `PrismaBookingAttendeeRepository.ts` 中，方法內的程式碼使用了單引號（`'@calcom/prisma/client'`），而專案規範 [R03] 要求使用雙引號。這可能導致 lint 或格式化檢查失敗。

建議將單引號改為雙引號。

**判斷依據**：diff 顯示 `PrismaBookingAttendeeRepository.ts` 的 import 使用單引號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:9</code> 檔案使用單引號，可能違反格式化規範</summary>

在 `PrismaBookingAttendeeRepository.ts` 中，方法內的程式碼使用了單引號（`'@calcom/prisma/client'`），而專案規範 [R03] 要求使用雙引號。這可能導致 lint 或格式化檢查失敗。

建議將單引號改為雙引號。

**判斷依據**：diff 顯示 `PrismaBookingAttendeeRepository.ts` 的 import 使用單引號。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16338 (cache hit 16256) ｜ completion tokens 2632 ｜ PR #3</sub>