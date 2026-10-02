<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程從直接使用 Prisma 改為注入 repository，並新增對應的 DI 模組與測試。主要風險在於 repository 介面與實作可能不完全匹配、部分查詢條件變更可能影響行為，以及新測試的覆蓋範圍有限。建議優先確認 BookingRepository 的 update 方法回傳型別與介面一致，並檢查取消後續預約時查詢條件是否正確。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/repositories/BookingRepository.ts:1509` | BookingRepository.update 回傳型別與 IBookingRepository 介面不符 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:513` | 取消後續預約時查詢條件可能遺漏部分預約 | 0.75 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 單一預約取消時改用 uid 作為唯一條件，可能忽略 id | 0.70 |
| 🔸 | Minor | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位可能影響其他功能 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:386` | 格式化變更可能違反 Biome 規則 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> BookingRepository.update 回傳型別與 IBookingRepository 介面不符</summary>

`IBookingRepository` 介面定義 `update` 回傳 `Promise<Booking>`，但實作回傳的是 `this.prismaClient.booking.update` 的結果，其型別為 `Prisma.Prisma__BookingClient<Booking>`，並非 `Booking`。這可能導致型別錯誤或執行時期行為不一致。建議在實作中加上 `await` 並明確回傳 `Booking`，或調整介面型別。

**判斷依據**：diff 中新增的 `update` 方法回傳 `await this.prismaClient.booking.update(...)`，而介面 `IBookingRepository` 定義 `update(...): Promise<Booking>`。Prisma 的 `update` 回傳的是 `PrismaPromise`，即使加上 `await` 也需確認型別是否完全符合。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:513</code> 取消後續預約時查詢條件可能遺漏部分預約</summary>

在取消後續預約的邏輯中，原本的 `findMany` 查詢條件為 `startTime: { gte: new Date() }`，但修改後改為 `gte: bookingToDelete.startTime`。若 `bookingToDelete.startTime` 早於目前時間，則可能包含已過去的預約；若晚於目前時間，則可能遺漏應取消的預約。建議確認此變更是否符合預期，或保留原本的 `new Date()` 條件。

**判斷依據**：diff 中原本的 `gte: new Date()` 被改為 `gte: bookingToDelete.startTime`，這可能改變查詢結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 單一預約取消時改用 uid 作為唯一條件，可能忽略 id</summary>

原本的 `where` 條件是 `uid ? { uid } : { id }`，修改後固定使用 `{ uid: bookingToDelete.uid }`。若 `bookingToDelete.uid` 可能為空或未定義，將導致查詢失敗或找不到預約。建議確認 `bookingToDelete.uid` 一定存在，或保留原本的條件邏輯。

**判斷依據**：diff 中原本的條件判斷被移除，改為直接使用 `uid`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位可能影響其他功能</summary>

`userSelect` 中移除了 `locale: true`，但 `handleCancelBooking` 中仍使用 `organizer.locale` 來取得翻譯。若 `UserRepository.findByIdOrThrow` 使用此 `userSelect`，則 `organizer.locale` 將為 `undefined`，可能導致翻譯回退到預設語言。建議確認 `findByIdOrThrow` 的實作是否包含 `locale`，或保留此欄位。

**判斷依據**：diff 中移除了 `locale: true`，但 `handleCancelBooking` 中仍使用 `organizer.locale`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:386</code> 格式化變更可能違反 Biome 規則</summary>

此處的縮排從原本的 8 空格改為 6 空格，可能不符合 Biome 的格式化規則（2 空格縮排）。建議執行 Biome 格式化確認。

**判斷依據**：diff 中縮排不一致，可能違反 R03。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16307 (cache hit 16256) ｜ completion tokens 1424 ｜ PR #3</sub>