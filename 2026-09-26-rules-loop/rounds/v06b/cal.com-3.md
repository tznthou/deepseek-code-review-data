<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取消預約流程中的 Prisma 直接呼叫改為透過 repository 注入，並新增對應的 repository 類別與 DI 模組。主要風險在於 BookingRepository 的 update 方法回傳型別與介面定義不一致，可能導致執行時錯誤；此外，部分 repository 類別仍使用全域 prisma 實例，未完全依賴注入，且新增的介面未完整定義既有方法，可能造成型別安全漏洞。建議優先修正 update 方法的型別問題，並補齊介面定義。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/repositories/BookingRepository.ts:1509` | BookingRepository.update 回傳型別與 IBookingRepository 介面不符 | 0.95 |
| ⚠️ | Major | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | BookingReferenceRepository 的既有靜態方法仍使用全域 prisma 實例 | 0.85 |
| ⚠️ | Major | `packages/features/profile/repositories/ProfileRepository.ts:1034` | ProfileRepository 的既有方法仍使用全域 prisma 實例 | 0.80 |
| ⚠️ | Major | `packages/lib/server/repository/dto/IBookingRepository.ts:46` | IBookingRepository 介面未包含所有既有方法 | 0.75 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:500` | updateMany 呼叫未處理回傳值 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1509</code> BookingRepository.update 回傳型別與 IBookingRepository 介面不符</summary>

`update` 方法回傳 `this.prismaClient.booking.update(...)`，其型別為 `Prisma.Prisma__BookingClient<Booking>`，但介面 `IBookingRepository` 宣告回傳 `Promise<Booking>`。這會導致型別錯誤，且若呼叫端依賴 Promise 的行為（例如 `await` 後直接使用屬性），可能因回傳的是 Prisma Promise 而非原生 Promise 而產生非預期行為。建議將介面回傳型別改為 `Prisma.Prisma__BookingClient<Booking>` 或將實作改為 `return await this.prismaClient.booking.update(...)` 以回傳 `Promise<Booking>`。

**判斷依據**：diff 中新增的 `update` 方法回傳 `await this.prismaClient.booking.update(...)`，但介面 `IBookingRepository` 定義回傳 `Promise<Booking>`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> BookingReferenceRepository 的既有靜態方法仍使用全域 prisma 實例</summary>

此 PR 將 `BookingReferenceRepository` 改為依賴注入 `prismaClient`，但既有的靜態方法（如 `findDailyVideoReferenceByRoomName`）仍使用全域 `prisma` 實例，而非注入的 `this.prismaClient`。這會導致在測試或需要隔離資料庫的環境中，這些方法仍存取全域連線，無法透過 DI 替換。建議將這些靜態方法改為實例方法，並使用 `this.prismaClient`。

**判斷依據**：diff 中新增建構子注入 `prismaClient`，但既有靜態方法仍使用 `prisma`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/profile/repositories/ProfileRepository.ts:1034</code> ProfileRepository 的既有方法仍使用全域 prisma 實例</summary>

`ProfileRepository` 新增了建構子注入 `prismaClient`，但既有的方法（如 `create`、`update` 等）仍使用全域 `prisma` 實例，而非注入的 `this.prismaClient`。這會導致在需要隔離資料庫的環境中，這些方法無法使用注入的連線。建議將所有方法改為使用 `this.prismaClient`。

**判斷依據**：diff 中新增 `findFirstByUserId` 使用 `this.prismaClient`，但其他方法仍使用全域 `prisma`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/server/repository/dto/IBookingRepository.ts:46</code> IBookingRepository 介面未包含所有既有方法</summary>

介面 `IBookingRepository` 僅定義了 `updateMany`、`update`、`findManyIncludeWorkflowRemindersAndReferences`，但 `BookingRepository` 類別還有許多其他方法（如 `getBookingForCalEventBuilder`、`findByIdIncludeDestinationCalendar` 等）。這會導致型別不安全，且未來若有人依賴此介面，可能無法存取完整功能。建議補齊所有方法簽章，或使用 `Pick` 等方式明確介面範圍。

**判斷依據**：介面中註解 `// ... Add existing methods as well here` 顯示未完整定義。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:500</code> updateMany 呼叫未處理回傳值</summary>

`bookingRepository.updateMany` 的回傳值（`{ count: number }`）被忽略，未檢查是否成功更新任何記錄。若因條件不符導致 count 為 0，程式仍會繼續執行，可能造成後續邏輯錯誤。建議檢查回傳值並在必要時拋出錯誤或記錄警告。

**判斷依據**：diff 中將原本的 `prisma.booking.updateMany` 改為 `bookingRepository.updateMany`，但未使用回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16328 (cache hit 16256) ｜ completion tokens 1630 ｜ PR #3</sub>