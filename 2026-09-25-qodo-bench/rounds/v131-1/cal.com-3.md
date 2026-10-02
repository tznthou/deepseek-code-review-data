<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預訂流程中的直接 Prisma 呼叫重構為依賴注入的 repository 類別，並新增了對應的介面與 DI 模組。整體方向正確，有助於解耦與測試。但存在幾個需要修正的問題：UserRepository 的 userSelect 移除了 locale 欄位，可能導致取消流程中取得翻譯時缺少 locale；BookingReferenceRepository 的既有靜態方法仍使用全域 prisma，未使用注入的 client，可能造成測試或交易問題；此外，部分 repository 方法缺少錯誤處理與交易包裝，且新增的測試僅驗證成功結果，未涵蓋失敗情境。建議優先修正 locale 欄位移除問題，並確認 repository 方法在取消流程中的一致性。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/users/repositories/UserRepository.ts:98` | 移除 locale 欄位可能導致取消流程中翻譯失敗 | 0.90 |
| ⚠️ | Major | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | 靜態方法仍使用全域 prisma，未使用注入的 client | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:498` | 取消後續預訂時使用 bookingToDelete.startTime 作為 gte 條件可能不正確 | 0.75 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 取消單一預訂時改用 uid 作為唯一條件可能導致錯誤 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法未回傳更新筆數 | 0.65 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1509` | update 方法未處理可能找不到預訂的情況 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 locale 欄位可能導致取消流程中翻譯失敗</summary>

在 `userSelect` 中移除了 `locale: true`，但取消流程中會使用 `organizer.locale` 來取得翻譯（`getTranslation(organizer.locale ?? "en", "common")`）。若 `locale` 欄位不再被選取，`organizer.locale` 將為 `undefined`，導致翻譯回退到英文，可能影響使用者體驗。請確認此變更是否為預期，或保留 `locale` 欄位。

**判斷依據**：diff 中顯示 `locale: true` 被移除，而 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> 靜態方法仍使用全域 prisma，未使用注入的 client</summary>

`findDailyVideoReferenceByRoomName` 等靜態方法仍直接使用全域 `prisma`，而非注入的 `this.prismaClient`。這可能導致在測試或需要交易隔離的場景中無法使用模擬的 client，且與新加入的實例方法不一致。建議將這些方法改為實例方法並使用 `this.prismaClient`，或提供靜態方法的替代方案。

**判斷依據**：diff 中新增了建構子與 `this.prismaClient`，但靜態方法仍使用全域 `prisma`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:498</code> 取消後續預訂時使用 bookingToDelete.startTime 作為 gte 條件可能不正確</summary>

在 `cancelSubsequentBookings` 為 true 時，原本使用 `new Date()` 作為 `gte` 條件，現在改為 `bookingToDelete.startTime`。這可能導致取消的範圍包含過去已完成的預訂，或遺漏了在 `bookingToDelete.startTime` 之後但已過去的預訂。請確認此變更是否符合業務邏輯。

**判斷依據**：diff 中將 `gte: new Date()` 改為 `gte: bookingToDelete.startTime`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 取消單一預訂時改用 uid 作為唯一條件可能導致錯誤</summary>

原本使用 `uid ? { uid } : { id }` 來決定更新條件，現在固定使用 `uid: bookingToDelete.uid`。若 `bookingToDelete.uid` 為空或未定義，將導致更新失敗。請確認 `bookingToDelete.uid` 在取消流程中一定存在，或保留原本的條件邏輯。

**判斷依據**：diff 中移除了原本的 `uid ? { uid } : { id }` 條件，改為固定使用 `uid`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法未回傳更新筆數</summary>

`updateMany` 方法未回傳 `count`，但介面 `IBookingRepository` 定義回傳 `Promise<{ count: number }>`。這可能導致呼叫端無法確認更新是否成功。建議回傳 `count` 或調整介面定義。

**判斷依據**：diff 中新增的 `updateMany` 方法沒有回傳值，但介面定義要求回傳 `{ count: number }`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> update 方法未處理可能找不到預訂的情況</summary>

`update` 方法直接呼叫 `prisma.booking.update`，若找不到符合條件的預訂會拋出例外。在取消流程中，若預訂已被刪除或不存在，可能導致未處理的錯誤。建議使用 `update` 的 `rejectOnNotFound` 選項或改用 `updateMany` 並檢查 `count`。

**判斷依據**：diff 中新增的 `update` 方法未處理找不到預訂的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14863 (cache hit 1408) ｜ completion tokens 1603 ｜ PR #3</sub>