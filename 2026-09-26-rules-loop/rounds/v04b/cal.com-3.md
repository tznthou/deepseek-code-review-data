<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預約流程中的 Prisma 直接呼叫重構為依賴注入的 repository 模式，並新增了對應的測試。整體方向正確，但存在幾個需要修正的問題：最嚴重的是 UserRepository 的 userSelect 移除了 locale 欄位，但取消流程中仍使用 organizer.locale，可能導致執行時錯誤；此外，BookingReferenceRepository 的既有靜態方法仍使用全域 prisma，未使用注入的 client，造成不一致；還有一些型別定義不完整、程式碼格式問題以及測試中缺少對資料庫狀態的斷言。建議先修正 locale 欄位問題，再處理其他項目。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/users/repositories/UserRepository.ts:98` | 移除 userSelect 中的 locale 欄位將導致取消流程中 organizer.locale 為 undefined | 0.95 |
| ⚠️ | Major | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | 既有靜態方法仍使用全域 prisma，未使用注入的 prismaClient | 0.85 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:500` | updateMany 的 where 條件中 startTime 使用 bookingToDelete.startTime 而非 new Date()，可能導致行為變更 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:546` | 單一預約取消時改用 uid 作為 where 條件，可能忽略 id 且未處理 uid 不存在的情況 | 0.80 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:473` | workflowReminders 型別定義不完整，可能缺少其他欄位 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:386` | 程式碼縮排不一致，可能違反格式化規範 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1056` | 新增測試僅驗證回傳值，未驗證資料庫狀態 | 0.70 |
| 🔸 | Minor | `packages/lib/server/repository/dto/IBookingRepository.ts:46` | 介面定義不完整，缺少既有方法的宣告 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 方法缺少回傳值型別，且未處理可能拋出的錯誤 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:147` | handler 函式中的 dependencies 預設值建立方式可能導致每次呼叫都建立新實例 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/users/repositories/UserRepository.ts:98</code> 移除 userSelect 中的 locale 欄位將導致取消流程中 organizer.locale 為 undefined</summary>

在 `handleCancelBooking.ts` 中，`organizer` 是透過 `userRepository.findByIdOrThrow` 取得，而 `UserRepository` 的 `userSelect` 原本包含 `locale: true`，但此 PR 將其移除。然而，取消流程中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`），這將導致 `organizer.locale` 為 `undefined`，進而可能回退到預設語言，但若其他程式碼直接使用 `organizer.locale` 而未提供預設值，則可能導致錯誤。此外，`findByIdOrThrow` 的回傳型別可能依賴 `locale` 欄位，移除後可能造成型別不符。建議保留 `locale: true` 或確保所有使用處都有預設值。

**判斷依據**：diff 中 `packages/features/users/repositories/UserRepository.ts` 的 `userSelect` 移除了 `locale: true`，但 `handleCancelBooking.ts` 中仍使用 `organizer.locale`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> 既有靜態方法仍使用全域 prisma，未使用注入的 prismaClient</summary>

`BookingReferenceRepository` 新增了建構子並注入 `prismaClient`，但既有的靜態方法（如 `findDailyVideoReferenceByRoomName`）仍使用全域的 `prisma`，而非注入的 client。這使得該 repository 在測試或不同環境中無法完全隔離，且與新的實例方法不一致。建議將這些靜態方法改為實例方法，或至少使用注入的 client。

**判斷依據**：diff 中 `BookingReferenceRepository` 新增了 `private prismaClient: PrismaClient;` 和建構子，但 `findDailyVideoReferenceByRoomName` 仍使用全域 `prisma`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:500</code> updateMany 的 where 條件中 startTime 使用 bookingToDelete.startTime 而非 new Date()，可能導致行為變更</summary>

在取消後續預約時，原本的 `where` 條件為 `startTime: { gte: new Date() }`，但重構後改為 `gte: bookingToDelete.startTime`。這可能導致取消範圍不同：如果 `bookingToDelete.startTime` 早於現在，則會包含過去已發生的預約；如果晚於現在，則可能遺漏部分應取消的預約。請確認此變更是否為預期行為，並考慮使用 `new Date()` 或明確的邏輯。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的 `updateMany` 呼叫，原本的 `gte: new Date()` 被改為 `gte: bookingToDelete.startTime`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:546</code> 單一預約取消時改用 uid 作為 where 條件，可能忽略 id 且未處理 uid 不存在的情況</summary>

原本的 `where` 條件是 `uid ? { uid } : { id }`，但重構後固定使用 `{ uid: bookingToDelete.uid }`。如果 `bookingToDelete.uid` 為空或未定義，則可能導致找不到預約或錯誤。此外，若同時有 id 和 uid，使用 uid 可能不是最佳選擇。建議保留原本的條件邏輯或確保 uid 一定存在。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的 `updateIncludeWorkflowRemindersAndReferences` 呼叫，原本的 `where` 條件被簡化為只使用 `uid`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:473</code> workflowReminders 型別定義不完整，可能缺少其他欄位</summary>

在 `updatedBookings` 的型別中，`workflowReminders` 被定義為 `{ id: number; referenceId: string | null; method: WorkflowMethods; }[]`，但實際的 `workflowReminders` 可能包含更多欄位（如 `scheduledDate`、`retryCount` 等）。這可能導致型別不匹配或後續使用時缺少必要資訊。建議使用 Prisma 的完整型別或明確列出所有需要的欄位。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的型別定義，只列出了三個欄位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:386</code> 程式碼縮排不一致，可能違反格式化規範</summary>

在 `team` 物件的縮排中，原本的縮排被改為較淺的縮排，與周圍程式碼不一致。這可能違反 Biome 的格式化規則（R03）。建議執行格式化工具修正。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的 `team` 物件縮排從原本的 8 空格改為 6 空格，與其他屬性不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking/test/handleCancelBooking.test.ts:1056</code> 新增測試僅驗證回傳值，未驗證資料庫狀態</summary>

新增的測試（如取消座位事件、取消後續預約等）只檢查了 `result.success` 等回傳值，但未驗證資料庫中的預約狀態、與會者是否被刪除、參考是否被標記為刪除等。這可能導致測試無法捕捉實際的資料庫操作錯誤。建議增加對資料庫狀態的斷言。

**判斷依據**：diff 中新增的測試區塊，每個測試都只有類似的斷言，未檢查資料庫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/lib/server/repository/dto/IBookingRepository.ts:46</code> 介面定義不完整，缺少既有方法的宣告</summary>

`IBookingRepository` 介面中只有 `updateMany`、`update`、`findManyIncludeWorkflowRemindersAndReferences` 三個方法，但 `BookingRepository` 類別還有許多其他方法（如 `findById`、`create` 等）。這可能導致型別檢查不完整，且未來擴充時容易遺漏。建議補齊所有需要的方法宣告，或使用 `Pick` 等方式。

**判斷依據**：diff 中 `IBookingRepository.ts` 的內容，只有三個方法，且註解提到要新增既有方法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 方法缺少回傳值型別，且未處理可能拋出的錯誤</summary>

`updateMany` 方法沒有明確的回傳型別（雖然 TypeScript 可以推斷），且未處理可能拋出的錯誤。建議加上 `Promise<{ count: number }>` 型別，並考慮是否需要錯誤處理。

**判斷依據**：diff 中 `BookingRepository.ts` 的 `updateMany` 方法，缺少回傳型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:147</code> handler 函式中的 dependencies 預設值建立方式可能導致每次呼叫都建立新實例</summary>

在 `handler` 函式中，如果未提供 `dependencies`，則會使用 `new UserRepository(prismaClient)` 等方式建立新的 repository 實例。這可能導致不必要的物件建立，且與依賴注入的初衷不符。建議考慮將預設依賴的建立移到模組層級或使用工廠函式。

**判斷依據**：diff 中 `handleCancelBooking.ts` 的 `handler` 函式，預設依賴在每次呼叫時建立。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15523 (cache hit 15488) ｜ completion tokens 2931 ｜ PR #3</sub>