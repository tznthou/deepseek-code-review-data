<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預訂流程中的 Prisma 直接呼叫重構為依賴注入的 repository，並新增了對應的介面與 DI 模組。整體方向正確，但存在幾個需要修正的問題：BookingReferenceRepository 的既有方法仍使用全域 prisma 實例，未使用注入的 prismaClient，可能導致測試與生產行為不一致；UserRepository 移除了 locale 欄位，但取消流程中仍使用 organizer.locale，可能造成執行時期錯誤；IBookingRepository 介面缺少 updateIncludeWorkflowRemindersAndReferences 方法，但實作類別有提供，型別契約不完整。建議優先修正這些問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | BookingReferenceRepository 既有方法仍使用全域 prisma 實例，未使用注入的 prismaClient | 0.95 |
| 🛑 | Blocker | `packages/features/users/repositories/UserRepository.ts:98` | UserRepository 移除 locale 欄位，但取消流程仍使用 organizer.locale | 0.90 |
| ⚠️ | Major | `packages/lib/server/repository/dto/IBookingRepository.ts:52` | IBookingRepository 介面缺少 updateIncludeWorkflowRemindersAndReferences 方法 | 0.85 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:500` | updateMany 呼叫未處理回傳值，可能忽略錯誤 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 單一預訂取消時改用 uid 作為唯一條件，可能忽略 id 參數 | 0.80 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:510` | findManyIncludeWorkflowRemindersAndReferences 的 where 條件可能包含不必要的 startTime 過濾 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:385` | 縮排不一致可能違反格式化規範 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> BookingReferenceRepository 既有方法仍使用全域 prisma 實例，未使用注入的 prismaClient</summary>

在建構子中注入了 prismaClient，但 `findDailyVideoReferenceByRoomName` 等既有方法仍直接使用全域 `prisma` 變數。這會導致在測試或需要隔離資料庫的場景中，repository 無法使用注入的 client，造成行為不一致。

**失敗情境**：當測試使用 mock 的 prismaClient 注入時，呼叫 `findDailyVideoReferenceByRoomName` 仍會存取真實資料庫，可能導致測試失敗或資料污染。

**建議**：將所有方法中的 `prisma` 替換為 `this.prismaClient`。

**判斷依據**：diff 中新增了建構子並注入 prismaClient，但既有方法仍使用全域 prisma。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> UserRepository 移除 locale 欄位，但取消流程仍使用 organizer.locale</summary>

在 `UserRepository` 的 `userSelect` 中移除了 `locale` 欄位，但在 `handleCancelBooking.ts` 中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`）。這會導致 `organizer.locale` 為 `undefined`，可能造成翻譯功能失效或執行時期錯誤。

**失敗情境**：當取消預訂時，`organizer.locale` 為 `undefined`，`getTranslation` 可能無法正確載入語言，或拋出錯誤。

**建議**：在 `userSelect` 中保留 `locale` 欄位，或在 `findByIdOrThrow` 的查詢中明確包含 `locale`。

**判斷依據**：diff 中移除了 `locale: true`，但 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/server/repository/dto/IBookingRepository.ts:52</code> IBookingRepository 介面缺少 updateIncludeWorkflowRemindersAndReferences 方法</summary>

`BookingRepository` 實作了 `updateIncludeWorkflowRemindersAndReferences` 方法，但 `IBookingRepository` 介面中未宣告此方法。這會導致型別契約不完整，使用介面型別的程式碼無法呼叫此方法，且可能隱藏實作不一致。

**失敗情境**：若其他程式碼依賴 `IBookingRepository` 型別，將無法使用 `updateIncludeWorkflowRemindersAndReferences`，造成編譯錯誤或需要型別斷言。

**建議**：在 `IBookingRepository` 中新增此方法的簽章。

**判斷依據**：diff 中 `BookingRepository` 新增了 `updateIncludeWorkflowRemindersAndReferences`，但介面中未包含。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:500</code> updateMany 呼叫未處理回傳值，可能忽略錯誤</summary>

`bookingRepository.updateMany` 的回傳值（包含 `count`）未被使用。雖然目前可能不需要，但忽略可能導致無法偵測更新失敗或更新筆數不符預期。

**失敗情境**：若更新條件錯誤導致 0 筆更新，程式仍會繼續執行，可能造成後續邏輯錯誤。

**建議**：檢查回傳的 `count`，必要時拋出錯誤或記錄警告。

**判斷依據**：diff 中新增了 `updateMany` 呼叫，但未使用其回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 單一預訂取消時改用 uid 作為唯一條件，可能忽略 id 參數</summary>

原本的 `where` 條件是 `uid ? { uid } : { id }`，現在改為固定使用 `{ uid: bookingToDelete.uid }`。若 `bookingToDelete.uid` 為空或未定義，將導致查詢失敗或更新錯誤的記錄。

**失敗情境**：若 `bookingToDelete.uid` 為 `null` 或 `undefined`，Prisma 會拋出錯誤，或更新到不正確的記錄。

**建議**：保留原本的條件邏輯，或確保 `bookingToDelete.uid` 一定存在。

**判斷依據**：diff 中將原本的條件式改為固定使用 uid。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:510</code> findManyIncludeWorkflowRemindersAndReferences 的 where 條件可能包含不必要的 startTime 過濾</summary>

在 `findManyIncludeWorkflowRemindersAndReferences` 的 `where` 中使用了 `startTime: { gte: bookingToDelete.startTime }`，但原本的程式碼是 `gte: new Date()`。這可能改變行為，特別是在處理過去或未來的預訂時。

**失敗情境**：若 `bookingToDelete.startTime` 是過去的時間，則會包含更多預訂；若是未來時間，則可能遺漏應取消的預訂。

**建議**：確認此變更是否符合預期，並考慮使用 `new Date()` 或明確的業務邏輯。

**判斷依據**：diff 中將原本的 `gte: new Date()` 改為 `gte: bookingToDelete.startTime`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:385</code> 縮排不一致可能違反格式化規範</summary>

在 `team` 物件的縮排中，原本的縮排被改為較淺的縮排，可能不符合專案的 Biome 格式化規則（2 空格縮排）。

**建議**：執行 Biome 格式化以確保一致性。

**判斷依據**：diff 中顯示縮排從原本的 8 空格改為 6 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16348 (cache hit 16256) ｜ completion tokens 2059 ｜ PR #3</sub>