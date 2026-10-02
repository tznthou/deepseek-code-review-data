<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程中的 Prisma 直接呼叫重構為依賴注入的 repository 模式，並新增對應的 repository 類別與介面。主要風險在於 UserRepository 的 userSelect 移除了 locale 欄位，可能導致取消流程中取得 organizer 時缺少 locale，進而影響翻譯或時區處理。此外，部分 repository 方法未完整實作介面，且新增的測試僅驗證成功結果，未涵蓋資料庫狀態驗證。建議優先確認 locale 欄位移除的影響，並補齊介面實作與測試斷言。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位可能導致取消流程缺少必要資訊 | 0.80 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:347` | BookingRepository 未完整實作 IBookingRepository 介面 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:513` | 取消後續預約時查詢條件可能包含已取消的預約 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1056` | 新增測試僅驗證成功結果，未驗證資料庫狀態 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位可能導致取消流程缺少必要資訊</summary>

在 `userSelect` 中移除了 `locale: true`，但取消流程中 `handler` 會使用 `organizer.locale` 來取得翻譯（`getTranslation(organizer.locale ?? "en", "common")`）。若 `UserRepository.findByIdOrThrow` 使用此 `userSelect`，則回傳的 organizer 物件將缺少 `locale` 屬性，導致翻譯永遠使用預設英文，或若型別未正確反映可能造成執行時期錯誤。

建議確認 `findByIdOrThrow` 是否使用此 `userSelect`，若取消流程需要 locale，則應保留該欄位或提供替代方式取得。

**判斷依據**：diff 中移除了 `locale: true`，而 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:347</code> BookingRepository 未完整實作 IBookingRepository 介面</summary>

`BookingRepository` 宣稱 `implements IBookingRepository`，但介面中定義了 `update` 方法，而類別中僅有 `updateMany` 和 `updateIncludeWorkflowRemindersAndReferences`，未提供名為 `update` 的方法。這可能導致 TypeScript 編譯錯誤，或未來使用介面時出現不一致。

建議補齊 `update` 方法或調整介面定義。

**判斷依據**：diff 中新增 `implements IBookingRepository`，但未見 `update` 方法實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:513</code> 取消後續預約時查詢條件可能包含已取消的預約</summary>

在 `cancelSubsequentBookings` 為 true 時，先執行 `bookingRepository.updateMany` 將符合條件的預約標記為取消，接著使用 `bookingRepository.findManyIncludeWorkflowRemindersAndReferences` 查詢相同條件（`startTime >= bookingToDelete.startTime`）的預約。由於查詢條件未排除已取消的預約，可能將剛取消的預約也包含在內，導致後續處理（如發送取消通知）重複執行。

建議在查詢條件中加入狀態過濾（例如 `status: { not: BookingStatus.CANCELLED }`）或調整查詢時機。

**判斷依據**：diff 中 `updateMany` 與 `findMany` 使用相同 where 條件，且未排除已取消狀態。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1056</code> 新增測試僅驗證成功結果，未驗證資料庫狀態</summary>

新增的四個測試均只檢查 `result.success` 和 `result.bookingId`，未驗證取消後資料庫中的實際狀態（例如預約狀態是否為 CANCELLED、attendee 是否刪除、booking reference 是否標記 deleted）。這使得測試無法有效捕捉 repository 實作中的錯誤。

建議在測試中加入對資料庫的查詢斷言，確認預期副作用已發生。

**判斷依據**：測試中僅有對 result 物件的斷言，未見對 prisma mock 的驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16338 (cache hit 16256) ｜ completion tokens 1264 ｜ PR #3</sub>