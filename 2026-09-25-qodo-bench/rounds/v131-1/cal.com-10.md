<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 整合了 booking audit 功能，在多個入口（API v2、magic link、webhook、tRPC）加入 actor 與 actionSource，並新增 MAGIC_LINK 來源與 bulk rejected 事件。主要風險在於 reject 流程中 oldStatus 的取得時機錯誤，可能導致 audit log 記錄不正確；另外 handleConfirmation 中單筆 accepted 的 oldStatus 被硬編碼為 ACCEPTED，同樣可能失真。建議優先修正這兩個資料正確性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468` | reject 單筆 booking 時 oldStatus 取得時機錯誤 | 0.90 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432` | recurring reject 流程中 oldStatus 取得時機錯誤 | 0.85 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 accepted 的 oldStatus 被硬編碼為 ACCEPTED | 0.80 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring accepted 流程中 oldStatus 可能不準確 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468</code> reject 單筆 booking 時 oldStatus 取得時機錯誤</summary>

在非 recurring 的 reject 流程中，`rejectedBookings` 的 `oldStatus` 取自 `booking.status`，但此時 `booking` 物件已在稍早的 `prisma.booking.update` 中被更新為 `REJECTED`，因此 `oldStatus` 會是 `REJECTED` 而非原本的 `PENDING`。這會導致 audit log 中的狀態變更記錄錯誤（old 和 new 都是 REJECTED）。

建議在更新前先保存原始狀態，例如：
```ts
const oldStatus = booking.status;
await prisma.booking.update({ ... });
rejectedBookings = [{ uid: booking.uid, oldStatus }];
```

**判斷依據**：diff 中新增的 `rejectedBookings` 指派位於 `prisma.booking.update` 之後，而 `booking` 物件在該 update 後已被修改。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432</code> recurring reject 流程中 oldStatus 取得時機錯誤</summary>

在 recurring reject 流程中，先以 `prisma.booking.updateMany` 將所有符合條件的 booking 更新為 `REJECTED`，之後才查詢 `updatedRecurringBookings` 並將其 `status` 作為 `oldStatus`。此時查詢到的狀態已經是 `REJECTED`，導致 audit log 的 `oldStatus` 錯誤。

建議在更新前先查詢並保存原始狀態，例如：
```ts
const unconfirmedRecurringBookings = await prisma.booking.findMany({ ... });
const oldStatuses = new Map(unconfirmedRecurringBookings.map(b => [b.uid, b.status]));
await prisma.booking.updateMany({ ... });
rejectedBookings = unconfirmedRecurringBookings.map(b => ({ uid: b.uid, oldStatus: oldStatuses.get(b.uid)! }));
```

**判斷依據**：diff 中 `updatedRecurringBookings` 查詢發生在 `updateMany` 之後，且 `oldStatus` 直接使用查詢結果的 `status`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 accepted 的 oldStatus 被硬編碼為 ACCEPTED</summary>

在非 recurring 的 accepted 流程中，`acceptedBookings` 的 `oldStatus` 被直接設定為 `BookingStatus.ACCEPTED`，但實際上 booking 在確認前可能是 `PENDING` 或其他狀態。這會導致 audit log 中的狀態變更記錄不正確。

建議在更新前取得 booking 的原始狀態，例如：
```ts
const oldStatus = booking.status;
// ... 更新 booking ...
acceptedBookings = [{ uid: booking.uid, oldStatus }];
```

**判斷依據**：diff 中 `acceptedBookings` 的 `oldStatus` 被硬編碼為 `BookingStatus.ACCEPTED`，未使用實際更新前的狀態。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring accepted 流程中 oldStatus 可能不準確</summary>

在 recurring accepted 流程中，`acceptedBookings` 的 `oldStatus` 取自 `unconfirmedRecurringBookings` 的 `status`，但該查詢僅篩選 `status: PENDING`，因此 `oldStatus` 會是 `PENDING`。若實際上有其他狀態的 booking 被更新（例如 `TENTATIVE`），則 audit log 會不正確。建議確認是否所有可能被更新的狀態都應被記錄，或調整查詢條件。

**判斷依據**：diff 中 `unconfirmedRecurringBookings` 查詢條件為 `status: BookingStatus.PENDING`，因此 `oldStatus` 只會是 `PENDING`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 29972 (cache hit 1408) ｜ completion tokens 1506 ｜ PR #10</sub>