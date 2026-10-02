<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程中的 Prisma 直接呼叫重構為依賴注入的 repository 模式，並新增對應的測試。主要風險在於 `BookingRepository.update` 方法未包含 `select`，可能回傳不完整的資料；`BookingReferenceRepository` 的靜態方法仍使用全域 `prisma`，可能造成測試與生產行為不一致；以及 `UserRepository` 移除了 `locale` 欄位，可能影響取消流程中的在地化。建議優先修正 `update` 方法的回傳型別與 `locale` 欄位的移除。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/repositories/BookingRepository.ts:1509` | BookingRepository.update 未包含 select，回傳資料不完整 | 0.80 |
| ⚠️ | Major | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | BookingReferenceRepository 靜態方法仍使用全域 prisma，可能造成測試與生產行為不一致 | 0.75 |
| ⚠️ | Major | `packages/features/users/repositories/UserRepository.ts:98` | UserRepository 移除 locale 欄位可能影響取消流程的在地化 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:500` | updateMany 回傳值未使用，可能隱藏錯誤 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 取消單一預約時改用 uid 作為唯一條件，可能忽略 id 參數 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> BookingRepository.update 未包含 select，回傳資料不完整</summary>

`update` 方法直接呼叫 `this.prismaClient.booking.update` 而未指定 `select`，因此回傳完整的 `Booking` 物件。然而，`IBookingRepository` 介面中此方法的回傳型別為 `Promise<Booking>`，但呼叫端 `handleCancelBooking` 中預期回傳的物件包含 `workflowReminders` 與 `references` 等關聯資料。這可能導致後續程式碼存取未定義的屬性而發生錯誤。

建議：在 `update` 方法中加入與 `updateIncludeWorkflowRemindersAndReferences` 相同的 `select`，或調整介面與呼叫端以符合實際回傳型別。

**判斷依據**：diff 中新增的 `update` 方法沒有 `select`，而 `IBookingRepository` 介面定義回傳 `Promise<Booking>`，但 `handleCancelBooking` 中呼叫 `bookingRepository.updateIncludeWorkflowRemindersAndReferences` 而非 `update`，但 `update` 仍可能被其他程式碼使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> BookingReferenceRepository 靜態方法仍使用全域 prisma，可能造成測試與生產行為不一致</summary>

`BookingReferenceRepository` 的靜態方法 `findDailyVideoReferenceByRoomName` 仍使用全域 `prisma` 實例，而非注入的 `prismaClient`。這使得在測試中無法替換資料庫客戶端，且與新加入的實例方法 `updateManyByBookingId` 使用注入的 `prismaClient` 不一致。

建議：將靜態方法改為實例方法，或將全域 `prisma` 改為使用注入的 `prismaClient`。

**判斷依據**：diff 中新增了建構子與 `prismaClient` 屬性，但靜態方法仍使用全域 `prisma`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> UserRepository 移除 locale 欄位可能影響取消流程的在地化</summary>

`userSelect` 中移除了 `locale: true`，這可能導致 `UserRepository.findByIdOrThrow` 回傳的使用者物件缺少 `locale` 屬性。在 `handleCancelBooking` 中，`organizer.locale` 被用於 `getTranslation(organizer.locale ?? "en", "common")`，若 `locale` 為 `undefined`，將一律使用英文翻譯，可能造成非英文使用者的通知語言錯誤。

建議：確認 `locale` 欄位是否仍需要，若需要則保留；若不需要，則應調整 `handleCancelBooking` 中的語言選擇邏輯。

**判斷依據**：diff 中移除了 `locale: true`，而 `handleCancelBooking` 中使用了 `organizer.locale`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:500</code> updateMany 回傳值未使用，可能隱藏錯誤</summary>

`bookingRepository.updateMany` 的回傳值（`{ count: number }`）未被使用。若更新影響的行數為 0，可能表示預期要取消的預約不存在或條件不符，但程式碼未檢查此情況，可能導致後續流程繼續執行而產生不一致狀態。

建議：檢查 `updateMany` 的回傳值，若 `count` 為 0 則記錄警告或拋出錯誤。

**判斷依據**：diff 中 `updateMany` 的呼叫未使用回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 取消單一預約時改用 uid 作為唯一條件，可能忽略 id 參數</summary>

原本的程式碼使用 `uid ? { uid } : { id }` 來決定唯一條件，但重構後直接使用 `{ uid: bookingToDelete.uid }`。若 `bookingToDelete.uid` 為空或未定義，可能導致查詢失敗或更新錯誤的記錄。

建議：保留原本的條件邏輯，或確保 `bookingToDelete.uid` 一定存在。

**判斷依據**：diff 中移除了原本的 `uid ? { uid } : { id }` 條件。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16348 (cache hit 14848) ｜ completion tokens 1628 ｜ PR #3</sub>