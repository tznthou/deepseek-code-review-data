<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將取消預約流程中的直接 Prisma 呼叫重構為注入 repository，並新增對應的 DI 模組與介面。主要風險在於 `BookingRepository.updateMany` 的回傳型別與介面定義不符、`BookingReferenceRepository` 的靜態方法仍使用全域 prisma 可能導致測試或交易問題，以及 `ProfileRepository` 的建構子變更可能影響其他使用靜態方法的程式碼。建議優先修正型別不一致與靜態方法依賴全域 prisma 的問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/repositories/BookingRepository.ts:1502` | updateMany 回傳型別與介面不符 | 0.80 |
| ⚠️ | Major | `packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24` | 靜態方法仍使用全域 prisma，可能繞過注入的 client | 0.70 |
| 🔸 | Minor | `packages/features/profile/repositories/ProfileRepository.ts:103` | ProfileRepository 建構子變更可能影響其他使用靜態方法的程式碼 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:136` | handler 函式依賴全域 prisma 作為 fallback | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:1502</code> updateMany 回傳型別與介面不符</summary>

`IBookingRepository` 介面定義 `updateMany` 回傳 `Promise<{ count: number }>`，但實作中直接回傳 `this.prismaClient.booking.updateMany(...)`，其回傳型別為 `Prisma.BatchPayload`（包含 `count` 屬性），但 TypeScript 可能因型別推斷而無法直接相容。建議明確標註回傳型別或調整介面定義。

**判斷依據**：介面定義於 `packages/lib/server/repository/dto/IBookingRepository.ts` 第 20 行，實作於 `packages/features/bookings/repositories/BookingRepository.ts` 第 344 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookingReference/repositories/BookingReferenceRepository.ts:24</code> 靜態方法仍使用全域 prisma，可能繞過注入的 client</summary>

`findDailyVideoReferenceByRoomName` 和 `replaceBookingReferences` 仍為靜態方法並使用全域 `prisma`，而新加入的 `updateManyByBookingId` 使用注入的 `prismaClient`。這可能導致在測試或需要交易隔離的場景中，部分操作使用不同的 client，造成資料不一致。建議將這些靜態方法改為實例方法並使用注入的 client。

**判斷依據**：diff 中新增了建構子與 `prismaClient` 屬性，但未修改靜態方法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/profile/repositories/ProfileRepository.ts:103</code> ProfileRepository 建構子變更可能影響其他使用靜態方法的程式碼</summary>

`ProfileRepository` 新增了建構子並要求注入 `prismaClient`，但類別中仍有大量靜態方法使用全域 `prisma`。若其他程式碼以 `new ProfileRepository()` 方式建立實例，將因缺少參數而失敗。建議確認所有建立實例的地方都已更新，或提供預設參數。

**判斷依據**：diff 中新增建構子，但未修改靜態方法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:136</code> handler 函式依賴全域 prisma 作為 fallback</summary>

`handler` 函式在未提供 `dependencies` 時，會使用全域 `prisma` 建立 repository 實例。這可能導致在測試或需要隔離的環境中，仍使用全域 client。建議明確要求傳入 dependencies，或提供更安全的預設值。

**判斷依據**：diff 中新增 fallback 邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 41539 (cache hit 41472) ｜ completion tokens 1161 ｜ PR #3</sub>