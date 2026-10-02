<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預約流程中的直接 Prisma 呼叫重構為依賴注入的 repository 模式，並新增對應的 repository 類別與介面。主要風險在於 `UserRepository` 的 `userSelect` 移除了 `locale` 欄位，可能導致後續程式碼存取 `organizer.locale` 時得到 undefined，進而影響翻譯或時區處理。此外，部分 repository 方法缺少回傳型別、介面定義不完整，以及測試中未驗證資料庫狀態，可能隱藏回歸問題。建議優先修正 `locale` 欄位的移除，並補齊型別與測試斷言。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位將導致 organizer.locale 為 undefined | 0.95 |
| ⚠️ | Major | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法缺少回傳型別 | 0.80 |
| ⚠️ | Major | `packages/lib/server/repository/dto/IBookingRepository.ts:46` | 介面 IBookingRepository 未包含 updateIncludeWorkflowRemindersAndReferences 方法 | 0.70 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:513` | 取消後續預約時查詢條件可能遺漏部分預約 | 0.70 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 取消單一預約時改用 uid 作為唯一條件，可能忽略 id | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1053` | 新增測試未驗證資料庫狀態，僅檢查回傳值 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:1` | 檔案格式不符合 Biome 規範（單引號、無分號） | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位將導致 organizer.locale 為 undefined</summary>

在 `UserRepository` 的 `userSelect` 中移除了 `locale: true`，但 `handleCancelBooking.ts` 中仍使用 `organizer.locale` 來取得翻譯：`const tOrganizer = await getTranslation(organizer.locale ?? "en", "common");`。由於 `findByIdOrThrow` 使用此 select，回傳的 organizer 物件將缺少 `locale` 屬性，導致 `organizer.locale` 為 undefined，最終 fallback 到 "en"，可能造成非英語使用者的通知或錯誤訊息語言錯誤。

建議：在 `userSelect` 中保留 `locale: true`，或確保 `findByIdOrThrow` 使用包含 locale 的 select。

**判斷依據**：diff 中 `packages/features/users/repositories/UserRepository.ts` 的 `userSelect` 移除了 `locale: true`，而 `handleCancelBooking.ts` 第 336 行使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法缺少回傳型別</summary>

`updateMany` 方法沒有標註回傳型別，雖然 TypeScript 可以推斷，但明確標註有助於維護與介面一致性。建議加上 `Promise<{ count: number }>`。

**判斷依據**：diff 中新增的 `updateMany` 方法缺少回傳型別，而介面 `IBookingRepository` 中定義為 `Promise<{ count: number }>`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/server/repository/dto/IBookingRepository.ts:46</code> 介面 IBookingRepository 未包含 updateIncludeWorkflowRemindersAndReferences 方法</summary>

`BookingRepository` 實作了 `updateIncludeWorkflowRemindersAndReferences` 方法，但 `IBookingRepository` 介面中未宣告此方法，導致型別契約不完整。建議在介面中補上此方法的簽名。

**判斷依據**：diff 中 `BookingRepository` 新增了 `updateIncludeWorkflowRemindersAndReferences`，但 `IBookingRepository` 未列出。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:513</code> 取消後續預約時查詢條件可能遺漏部分預約</summary>

在取消後續預約的邏輯中，原本的 `findMany` 查詢使用 `startTime: { gte: new Date() }`，但重構後改為 `gte: bookingToDelete.startTime`。這可能導致如果 `bookingToDelete.startTime` 早於當前時間，會包含已過去的預約；反之若晚於當前時間，則可能遺漏應取消的預約。請確認此變更是否符合預期。

**判斷依據**：diff 中原本的 `gte: new Date()` 被改為 `gte: bookingToDelete.startTime`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 取消單一預約時改用 uid 作為唯一條件，可能忽略 id</summary>

原本的 `where` 條件是 `uid ? { uid } : { id }`，但重構後固定使用 `uid: bookingToDelete.uid`。如果 `bookingToDelete.uid` 為 undefined 或空字串，將導致查詢失敗或找不到記錄。請確認 `bookingToDelete.uid` 在此情境下一定存在。

**判斷依據**：diff 中原本的條件判斷被移除，改為直接使用 `uid`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1053</code> 新增測試未驗證資料庫狀態，僅檢查回傳值</summary>

新增的四個測試都只檢查 `result.success`、`result.onlyRemovedAttendee` 和 `result.bookingId`，沒有驗證資料庫中的預約狀態、出席者是否刪除、參考是否標記刪除等。這可能無法捕捉到實際的資料變更錯誤。建議加入對資料庫狀態的斷言。

**判斷依據**：diff 中新增的測試僅有回傳值斷言，未查詢資料庫驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/PrismaBookingAttendeeRepository.ts:1</code> 檔案格式不符合 Biome 規範（單引號、無分號）</summary>

此新檔案使用單引號且缺少分號，與專案其他檔案的雙引號和分號風格不一致，可能違反 R03。建議執行 Biome 格式化。

**判斷依據**：diff 中新增的檔案使用單引號且無分號，與其他檔案風格不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16338 (cache hit 1536) ｜ completion tokens 2071 ｜ PR #3</sub>