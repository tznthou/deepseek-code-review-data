<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程中的直接 Prisma 呼叫重構為依賴注入的 repository 模式，並新增了對應的測試。主要風險在於 repository 介面定義不完整、部分方法仍使用全域 prisma 實例、以及測試中可能存在非預期的副作用。建議優先修正 BookingReferenceRepository 中靜態方法未使用注入的 prismaClient 的問題，並補齊介面定義。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | 靜態方法仍使用全域 prisma 實例，未使用注入的 prismaClient | 0.90 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:140` | handler 中仍使用全域 prisma 實例作為預設依賴 | 0.85 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:500` | updateMany 呼叫未處理回傳值，可能遺漏錯誤 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 取消單一預約時改用 uid 作為唯一條件，可能忽略 id 參數 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:639` | bookingReferenceRepository.updateManyByBookingId 未處理錯誤 | 0.80 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:473` | workflowReminders 型別定義與實際查詢可能不符 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未回傳 Prisma 的 BatchPayload | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未回傳 Prisma 的 BatchPayload | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:140` | handler 中仍使用全域 prisma 實例作為預設依賴 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:500` | updateMany 呼叫未處理回傳值，可能遺漏錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> 靜態方法仍使用全域 prisma 實例，未使用注入的 prismaClient</summary>

`findDailyVideoReferenceByRoomName` 和 `findByBookingId` 等靜態方法仍直接使用全域 `prisma`，而非建構子注入的 `this.prismaClient`。這會導致在測試或需要替換資料庫連線的場景下，這些方法仍存取全域實例，破壞依賴注入的隔離性。建議將這些方法改為實例方法，並使用 `this.prismaClient`。

**判斷依據**：diff 中新增了建構子與 `this.prismaClient`，但原有的靜態方法仍使用 `prisma` 全域變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:140</code> handler 中仍使用全域 prisma 實例作為預設依賴</summary>

在 `handler` 函式中，當 `dependencies` 未提供時，會使用全域 `prisma` 建立 repository 實例。這使得測試或未來需要替換資料庫連線時，仍會依賴全域實例。建議將 `prisma` 也透過依賴注入傳入，或提供一個明確的預設實例來源。

**判斷依據**：diff 中顯示 `const prismaClient = prisma;` 並用於建立 repository，但 `prisma` 是全域匯入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:500</code> updateMany 呼叫未處理回傳值，可能遺漏錯誤</summary>

`await bookingRepository.updateMany(...)` 的回傳值（包含受影響的資料列數）未被檢查。若更新失敗或影響 0 列，程式仍會繼續執行，可能導致後續邏輯基於錯誤假設。建議檢查回傳值並在必要時拋出錯誤或記錄警告。

**判斷依據**：diff 中新增了 `updateMany` 呼叫，但未使用其回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 取消單一預約時改用 uid 作為唯一條件，可能忽略 id 參數</summary>

原本的 `where` 條件會根據 `uid` 或 `id` 擇一使用，但重構後固定使用 `uid: bookingToDelete.uid`。若呼叫端僅提供 `id` 而未提供 `uid`，或 `uid` 與 `id` 不一致，可能導致更新錯誤的預約或找不到預約。建議保留原本的條件邏輯，或明確驗證 `uid` 的存在。

**判斷依據**：diff 中刪除了原本的 `const where: Prisma.BookingWhereUniqueInput = uid ? { uid } : { id };`，並改為固定使用 `uid`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:639</code> bookingReferenceRepository.updateManyByBookingId 未處理錯誤</summary>

`await bookingReferenceRepository.updateManyByBookingId(bookingToDelete.id, { deleted: true });` 被包在 try-catch 中，但 catch 區塊僅記錄錯誤，未重新拋出或採取補救措施。這可能導致部分參考資料未被標記刪除，但流程仍繼續，造成資料不一致。建議評估是否需要更嚴格的錯誤處理。

**判斷依據**：diff 中顯示此呼叫在 try 區塊內，且 catch 僅記錄錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:473</code> workflowReminders 型別定義與實際查詢可能不符</summary>

`updatedBookings` 的型別中 `workflowReminders` 定義為 `{ id: number; referenceId: string | null; method: WorkflowMethods; }[]`，但實際查詢的 select 可能包含其他欄位（如 `referenceId` 的型別可能為 `string | null`）。建議確認型別與實際查詢結果一致，避免執行時期錯誤。

**判斷依據**：diff 中修改了 `workflowReminders` 的型別，但未確認與 repository 方法的回傳型別完全匹配。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未回傳 Prisma 的 BatchPayload</summary>

`updateMany` 方法目前回傳 `void`，但 Prisma 的 `updateMany` 通常回傳 `{ count: number }`。這使得呼叫端無法得知受影響的資料列數，可能隱藏更新失敗或影響範圍不符預期的問題。建議回傳 `Promise<{ count: number }>`。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳任何值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未回傳 Prisma 的 BatchPayload</summary>

`updateMany` 方法目前回傳 `void`，但 Prisma 的 `updateMany` 通常回傳 `{ count: number }`。這使得呼叫端無法得知受影響的資料列數，可能隱藏更新失敗或影響範圍不符預期的問題。建議回傳 `Promise<{ count: number }>`。

**判斷依據**：diff 中新增的 `updateMany` 方法未回傳任何值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:140</code> handler 中仍使用全域 prisma 實例作為預設依賴</summary>

在 `handler` 函式中，當 `dependencies` 未提供時，會使用全域 `prisma` 建立 repository 實例。這使得測試或未來需要替換資料庫連線時，仍會依賴全域實例。建議將 `prisma` 也透過依賴注入傳入，或提供一個明確的預設實例來源。

**判斷依據**：diff 中顯示 `const prismaClient = prisma;` 並用於建立 repository，但 `prisma` 是全域匯入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:500</code> updateMany 呼叫未處理回傳值，可能遺漏錯誤</summary>

`await bookingRepository.updateMany(...)` 的回傳值（包含受影響的資料列數）未被檢查。若更新失敗或影響 0 列，程式仍會繼續執行，可能導致後續邏輯基於錯誤假設。建議檢查回傳值並在必要時拋出錯誤或記錄警告。

**判斷依據**：diff 中新增了 `updateMany` 呼叫，但未使用其回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16328 (cache hit 14848) ｜ completion tokens 2746 ｜ PR #3</sub>