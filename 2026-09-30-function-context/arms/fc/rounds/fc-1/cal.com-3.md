<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程中的直接 Prisma 呼叫重構為依賴注入的 repository 模式，並新增多個 repository 與 DI 模組。主要風險在於 `BookingReferenceRepository` 的靜態方法仍使用全域 `prisma`，可能繞過注入的 client；`BookingRepository` 的 `updateMany` 回傳型別與介面不一致；以及 `UserRepository` 的 `userSelect` 移除了 `locale` 欄位，可能影響取消流程中取得 organizer locale 的邏輯。建議優先修正上述問題，並補齊介面定義與測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | 靜態方法仍使用全域 prisma，可能繞過注入的 client | 0.80 |
| ⚠️ | Major | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 回傳型別與介面不一致 | 0.75 |
| ⚠️ | Major | `packages/features/users/repositories/UserRepository.ts:83` | 移除 userSelect 中的 locale 欄位可能影響取消流程 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:89` | Dependencies 型別使用具體類別而非介面 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:140` | handler 中仍直接使用全域 prisma | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> 靜態方法仍使用全域 prisma，可能繞過注入的 client</summary>

`findDailyVideoReferenceByRoomName` 和 `replaceBookingReferences` 仍為靜態方法，內部直接使用全域 `prisma`，而非注入的 `this.prismaClient`。這會導致在測試或需要替換資料庫連線的場景中，這些方法無法使用注入的 client，可能造成資料不一致或測試困難。建議將這些方法改為實例方法，並改用 `this.prismaClient`。

**判斷依據**：diff 中新增了建構子與 `this.prismaClient`，但靜態方法仍直接使用全域 `prisma`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 回傳型別與介面不一致</summary>

`IBookingRepository` 介面定義 `updateMany` 回傳 `Promise<{ count: number }>`，但實作中 `updateMany` 沒有回傳值（`await` 後未回傳）。這會導致呼叫端若依賴回傳值會得到 `undefined`，可能造成執行時期錯誤。建議讓實作回傳 `{ count }` 或調整介面。

**判斷依據**：介面定義於 `packages/lib/server/repository/dto/IBookingRepository.ts`，實作未回傳。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/users/repositories/UserRepository.ts:83</code> 移除 userSelect 中的 locale 欄位可能影響取消流程</summary>

`userSelect` 中移除了 `locale: true`，但 `handleCancelBooking.ts` 中呼叫 `userRepository.findByIdOrThrow` 取得 organizer 後，使用 `organizer.locale` 來取得翻譯。若 `findByIdOrThrow` 使用此 `userSelect`，則 `organizer.locale` 將為 `undefined`，可能導致翻譯失敗或錯誤。請確認 `findByIdOrThrow` 的實作是否包含 `locale`，或保留此欄位。

**判斷依據**：diff 中刪除了 `locale: true`，而 `handleCancelBooking.ts` 中仍有 `organizer.locale` 的使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:89</code> Dependencies 型別使用具體類別而非介面</summary>

`Dependencies` 型別中直接使用具體類別（如 `UserRepository`、`BookingRepository`），而非介面（如 `IUserRepository`、`IBookingRepository`）。這會降低可測試性與彈性，未來若要替換實作會較困難。建議改用介面型別。

**判斷依據**：diff 中新增的型別定義。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:140</code> handler 中仍直接使用全域 prisma</summary>

在 `handler` 函式中，仍有直接使用全域 `prisma` 的地方（如 `const prismaClient = prisma;`），這與重構目標（注入 repository）不一致。雖然目前作為 fallback，但可能造成混淆。建議完全移除直接使用，或明確標註為過渡方案。

**判斷依據**：diff 中新增了 `const prismaClient = prisma;`，但後續未使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 41539 (cache hit 1536) ｜ completion tokens 1314 ｜ PR #3</sub>