<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預約流程從直接使用 Prisma 改為注入 repository，並新增多個 repository 與 DI 模組。主要風險在於 `BookingRepository.updateMany` 的回傳型別與介面定義不符、`BookingCancelService` 的相依注入可能未正確傳遞、以及 `UserRepository` 移除 `locale` 欄位可能影響取消流程的翻譯功能。建議先修正型別與相依注入問題，並確認 `locale` 移除的影響。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 回傳型別與介面 IBookingRepository 不符 | 0.95 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:724` | BookingCancelService 的相依注入可能未正確傳遞 | 0.85 |
| ⚠️ | Major | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位可能影響取消流程的翻譯 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:500` | updateMany 呼叫未處理回傳值，可能遺漏錯誤 | 0.75 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 取消單一 booking 時改用 uid 作為 where 條件，可能忽略 id | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 回傳型別與介面 IBookingRepository 不符</summary>

`BookingRepository.updateMany` 實作呼叫 `this.prismaClient.booking.updateMany`，其回傳型別為 `Prisma.BatchPayload`（包含 `count`），但介面 `IBookingRepository` 定義此方法應回傳 `Promise<{ count: number }>`。目前實作未明確標註回傳型別，TypeScript 可能推斷為 `Promise<Prisma.BatchPayload>`，導致型別不相容。

**失敗情境**：當其他程式碼依賴 `IBookingRepository` 介面並期望 `updateMany` 回傳 `{ count: number }` 時，若實作回傳 `BatchPayload`（可能包含其他屬性），可能造成型別錯誤或執行期意外。

**建議**：在 `updateMany` 方法上明確標註回傳型別為 `Promise<{ count: number }>`，並確保回傳值符合介面。

**判斷依據**：diff 中新增的 `updateMany` 方法沒有回傳值，但介面 `IBookingRepository` 定義 `updateMany(params: { where: BookingWhereInput; data: BookingUpdateData }): Promise<{ count: number }>;`

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:724</code> BookingCancelService 的相依注入可能未正確傳遞</summary>

`BookingCancelService` 的建構子現在接受多個 repository 參數，並將它們傳給 `super`。但 `handler` 函式在沒有提供 `dependencies` 時會自行建立預設 repository 實例。若 `BookingCancelService` 的 `deps` 未正確設定，可能導致使用全域 `prisma` 而非注入的 client。

**失敗情境**：在測試或特定環境中，若 `BookingCancelService` 未正確注入 repository，取消流程可能使用錯誤的資料庫連線，導致資料不一致。

**建議**：確認 `BookingCancelService` 的 DI 設定正確，並考慮在 `handler` 中強制要求 `dependencies` 參數，避免意外使用全域 prisma。

**判斷依據**：diff 中 `BookingCancelService` 的 `cancel` 方法呼叫 `handler(cancelBookingInput, this.deps)`，但 `handler` 的 `dependencies` 參數是可選的，若未傳入會使用全域 prisma。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位可能影響取消流程的翻譯</summary>

`UserRepository` 的 `userSelect` 移除了 `locale` 欄位。在取消流程中，`organizer` 是透過 `userRepository.findByIdOrThrow` 取得，並使用 `organizer.locale` 來決定翻譯語言。若 `locale` 不再被選取，`organizer.locale` 將為 `undefined`，導致翻譯回退到預設語言。

**失敗情境**：當 organizer 的 locale 非預設語言時，取消通知的翻譯可能不正確。

**建議**：確認 `findByIdOrThrow` 的回傳型別是否包含 `locale`，若需要則保留此欄位，或改用其他方式取得 locale。

**判斷依據**：diff 中 `userSelect` 移除了 `locale: true`，但 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:500</code> updateMany 呼叫未處理回傳值，可能遺漏錯誤</summary>

`bookingRepository.updateMany` 的回傳值未被使用。若更新失敗（例如資料庫錯誤），錯誤可能被忽略，導致取消流程繼續執行，造成資料不一致。

**失敗情境**：當大量取消 recurring bookings 時，若 `updateMany` 因故失敗，程式不會拋出錯誤，後續步驟仍會執行，可能導致部分 booking 未被取消。

**建議**：檢查 `updateMany` 的回傳值（例如 `count`），或確保錯誤會被正確拋出並處理。

**判斷依據**：diff 中 `updateMany` 呼叫沒有接住回傳值或錯誤處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 取消單一 booking 時改用 uid 作為 where 條件，可能忽略 id</summary>

原本的 `where` 條件是 `uid ? { uid } : { id }`，現在改為固定使用 `{ uid: bookingToDelete.uid }`。若 `bookingToDelete.uid` 為空或未定義，可能導致查詢失敗。

**失敗情境**：若 booking 的 uid 為 null（例如舊資料），取消時會嘗試以 `uid: null` 查詢，可能找不到 booking 或拋出錯誤。

**建議**：保留原本的條件邏輯，或確保 `bookingToDelete.uid` 一定存在。

**判斷依據**：diff 中 `where` 條件從 `uid ? { uid } : { id }` 改為固定 `{ uid: bookingToDelete.uid }`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16338 (cache hit 14848) ｜ completion tokens 1799 ｜ PR #3</sub>