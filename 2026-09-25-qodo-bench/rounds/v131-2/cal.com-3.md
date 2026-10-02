<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程中的直接 Prisma 呼叫重構為依賴注入的 repository 模式，新增多個 repository 類別與介面，並調整 DI 模組。主要風險在於 UserRepository 的 userSelect 移除了 locale 欄位，可能導致取消流程中取得 organizer 時缺少 locale，進而影響翻譯或時區處理。此外，部分 repository 方法回傳型別與介面定義不一致，且新增的測試僅驗證成功結果，未涵蓋資料庫狀態或錯誤情境。建議優先確認 locale 移除的影響，並補齊型別與測試。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位可能導致取消流程缺少 locale | 0.80 |
| ⚠️ | Major | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未回傳 count，與介面定義不符 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1509` | update 方法回傳型別可能與介面不符 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:497` | 取消後續預約時，gte 條件從 new Date() 改為 bookingToDelete.startTime，可能遺漏同時開始的預約 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 取消單一預約時，where 條件從 uid 或 id 改為僅 uid，可能導致找不到預約 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1056` | 新增測試僅驗證成功結果，未驗證資料庫狀態或副作用 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位可能導致取消流程缺少 locale</summary>

在 `handleCancelBooking.ts` 中，organizer 是透過 `userRepository.findByIdOrThrow` 取得，而後續使用 `organizer.locale` 來取得翻譯（`getTranslation(organizer.locale ?? "en", "common")`）。此 PR 從 `userSelect` 中移除了 `locale` 欄位，若 `findByIdOrThrow` 使用此 select，則回傳的 organizer 物件將不再包含 `locale`，導致翻譯永遠回退到英文，或可能因型別錯誤而在執行時期出錯。

建議：確認 `findByIdOrThrow` 的實作是否使用 `userSelect`，若需要 locale，應保留該欄位或改用其他方式取得。

**判斷依據**：diff 顯示從 userSelect 中刪除了 `locale: true`，而 handleCancelBooking.ts 中仍使用 organizer.locale。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未回傳 count，與介面定義不符</summary>

`IBookingRepository` 介面定義 `updateMany` 應回傳 `Promise<{ count: number }>`，但實作中 `updateMany` 方法沒有回傳值（void）。這可能導致呼叫端依賴 count 時出現 undefined 錯誤。

建議：讓 `updateMany` 回傳 `this.prismaClient.booking.updateMany` 的結果，或調整介面定義。

**判斷依據**：diff 中新增的 updateMany 方法沒有 return，而 IBookingRepository 介面要求回傳 { count: number }。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> update 方法回傳型別可能與介面不符</summary>

`IBookingRepository` 定義 `update` 回傳 `Promise<Booking>`，但實作中 `update` 回傳 `this.prismaClient.booking.update` 的結果，其型別可能包含額外的關聯或欄位，不一定完全符合 `Booking` 型別。若型別不符，可能導致編譯錯誤或執行時期問題。

建議：確認 Prisma 回傳型別與介面一致，必要時使用型別斷言或調整介面。

**判斷依據**：介面 IBookingRepository 定義 update 回傳 Promise<Booking>，但實作直接回傳 Prisma 更新結果。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:497</code> 取消後續預約時，gte 條件從 new Date() 改為 bookingToDelete.startTime，可能遺漏同時開始的預約</summary>

原本使用 `gte: new Date()` 來取消所有未來（含現在）的預約，現在改為 `gte: bookingToDelete.startTime`。如果有多個預約具有相同的 startTime，且其中一個是 bookingToDelete，則其他相同 startTime 的預約可能不會被取消（因為 gte 包含等於，但 bookingToDelete 本身已被排除？）。需要確認此變更是否為預期行為。

建議：確認取消後續預約的語意，若應包含所有同時開始的預約，則應使用 `gte: bookingToDelete.startTime` 並確保排除自身，或保留原邏輯。

**判斷依據**：diff 顯示 gte 條件從 new Date() 改為 bookingToDelete.startTime。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 取消單一預約時，where 條件從 uid 或 id 改為僅 uid，可能導致找不到預約</summary>

原本使用 `where: uid ? { uid } : { id }`，現在固定使用 `{ uid: bookingToDelete.uid }`。如果 bookingToDelete.uid 為空或未定義，則會導致錯誤。雖然 bookingToDelete 應該總是有 uid，但若資料異常可能出錯。

建議：保留原本的 fallback 邏輯，或確保 uid 一定存在。

**判斷依據**：diff 顯示 where 條件從動態選擇改為固定使用 uid。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1056</code> 新增測試僅驗證成功結果，未驗證資料庫狀態或副作用</summary>

新增的四個測試都只檢查 `result.success`、`result.onlyRemovedAttendee` 和 `result.bookingId`，沒有驗證資料庫中的預約狀態、出席者是否被刪除、booking reference 是否被標記刪除等關鍵副作用。這可能讓錯誤的實作通過測試。

建議：增加對資料庫狀態的斷言，例如查詢預約狀態、出席者數量、reference 的 deleted 欄位等。

**判斷依據**：測試中僅有這三個 expect，沒有其他資料庫驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14863 (cache hit 14848) ｜ completion tokens 1927 ｜ PR #3</sub>