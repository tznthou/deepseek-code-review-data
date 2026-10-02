<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預約流程中的 Prisma 直接呼叫重構為依賴注入的 repository 模式，並新增了多個 repository 類別與介面。主要風險在於 `BookingRepository` 中的 `update` 方法未包含 select，可能導致回傳型別與介面不符；`UserRepository` 移除了 `locale` 欄位，但取消流程仍使用 `organizer.locale`，可能造成執行時錯誤；`BookingReferenceRepository` 的靜態方法仍使用全域 prisma，未完全依賴注入；以及測試中未驗證資料庫狀態，僅檢查回傳值，可能遺漏實際行為錯誤。建議優先修正 `update` 方法的 select 問題與 `locale` 欄位移除的影響。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/repositories/BookingRepository.ts:1509` | `update` 方法未包含 select，回傳型別與介面不符 | 0.95 |
| 🛑 | Blocker | `packages/features/users/repositories/UserRepository.ts:98` | 移除 `locale` 欄位可能導致取消流程執行時錯誤 | 0.90 |
| ⚠️ | Major | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | 靜態方法仍使用全域 prisma，未完全依賴注入 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:517` | `gte` 條件從 `new Date()` 改為 `bookingToDelete.startTime` 可能改變行為 | 0.75 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1056` | 測試僅驗證回傳值，未驗證資料庫狀態 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> `update` 方法未包含 select，回傳型別與介面不符</summary>

`IBookingRepository` 介面要求 `update` 回傳 `Promise<Booking>`，但此實作直接呼叫 `this.prismaClient.booking.update` 而未指定 `select`，因此會回傳完整的 `Booking` 型別。然而，`Booking` 型別可能包含關聯欄位（如 `references`、`workflowReminders`），而 Prisma 的 `update` 預設不會載入關聯，導致回傳物件缺少這些屬性，型別上卻宣稱有，造成執行時錯誤。此外，此方法在取消流程中被呼叫（`bookingRepository.updateIncludeWorkflowRemindersAndReferences` 才是正確用法），若誤用此方法可能取得不完整的資料。建議在 `update` 方法中加入明確的 `select`，或調整介面型別以符合實際回傳。

**判斷依據**：diff 中新增的 `update` 方法（行 1512-1517）沒有 `select`，而介面 `IBookingRepository` 定義 `update` 回傳 `Promise<Booking>`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 `locale` 欄位可能導致取消流程執行時錯誤</summary>

`UserRepository` 的 `userSelect` 中移除了 `locale: true`，但取消流程中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`）。這會導致 `organizer.locale` 為 `undefined`，雖然有 fallback 到 `"en"`，但可能不是預期行為，且若其他程式碼依賴 `locale` 欄位，將造成錯誤。建議確認所有使用 `UserRepository` 的地方是否都需要 `locale`，若需要則保留，或改用其他方式取得。

**判斷依據**：diff 中 `UserRepository.ts` 的 `userSelect` 移除了 `locale: true`，而 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> 靜態方法仍使用全域 prisma，未完全依賴注入</summary>

`BookingReferenceRepository` 新增了實例方法 `updateManyByBookingId`，但原有的靜態方法（如 `findDailyVideoReferenceByRoomName`）仍使用全域 `prisma` 物件，而非注入的 `prismaClient`。這使得測試時無法替換資料庫客戶端，且與本次重構的依賴注入方向不一致。建議將這些靜態方法改為實例方法，或至少使用注入的 `prismaClient`。

**判斷依據**：diff 中 `BookingReferenceRepository` 的建構子新增了 `prismaClient`，但靜態方法仍使用全域 `prisma`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:517</code> `gte` 條件從 `new Date()` 改為 `bookingToDelete.startTime` 可能改變行為</summary>

在取消後續預約的邏輯中，原本使用 `gte: new Date()` 來選取所有未來預約，現在改為 `gte: bookingToDelete.startTime`。這可能導致包含與目前預約相同開始時間的其他預約也被取消，或遺漏了在 `bookingToDelete.startTime` 之後但早於 `new Date()` 的預約（若目前時間已超過該開始時間）。需確認此變更是否符合預期，特別是在處理重複預約時。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的 `findManyIncludeWorkflowRemindersAndReferences` 呼叫中，`gte` 從 `new Date()` 改為 `bookingToDelete.startTime`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1056</code> 測試僅驗證回傳值，未驗證資料庫狀態</summary>

新增的測試案例（如取消座位事件、重複預約等）僅檢查 `result.success`、`result.onlyRemovedAttendee` 和 `result.bookingId`，未驗證資料庫中的實際變更（例如與會者是否被刪除、預約狀態是否更新）。這可能導致測試通過但實際行為錯誤。建議加入對資料庫狀態的斷言，例如查詢相關記錄確認已正確更新或刪除。

**判斷依據**：diff 中新增的測試案例僅有回傳值斷言，未見資料庫查詢驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15523 (cache hit 14848) ｜ completion tokens 1660 ｜ PR #3</sub>