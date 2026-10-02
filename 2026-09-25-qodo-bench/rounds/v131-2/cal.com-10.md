<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 整合了 booking audit 功能，新增了 actor 與 actionSource 的傳遞，並在確認/拒絕預訂時觸發審計事件。主要風險在於 `handleConfirmation` 中 `acceptedBookings` 的狀態可能不正確，以及 `handlePaymentSuccess` 的簽名變更可能影響其他呼叫點。建議先修正 `acceptedBookings` 的 oldStatus 設定，並確認所有呼叫點已更新。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單一預訂確認時 acceptedBookings 的 oldStatus 可能不正確 | 0.90 |
| ⚠️ | Major | `packages/app-store/_utils/payments/handlePaymentSuccess.ts:36` | handlePaymentSuccess 簽名變更可能導致其他呼叫點未更新 | 0.80 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring 預訂的 acceptedBookings 可能包含非 PENDING 狀態的預訂 | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468` | 單一預訂拒絕時 rejectedBookings 的 oldStatus 可能不正確 | 0.70 |
| 🔸 | Minor | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 schema 變更可能影響既有資料 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單一預訂確認時 acceptedBookings 的 oldStatus 可能不正確</summary>

在非 recurring 的單一預訂確認流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此處的 `booking` 是從資料庫取得的原始預訂，其狀態在確認前可能是 `PENDING` 或其他非 `ACCEPTED` 狀態。這會導致審計事件中的 `oldStatus` 錯誤，影響審計記錄的準確性。

建議：應使用更新前的實際狀態，例如從 `booking.status` 取得，或先查詢再更新。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation.ts 的單一預訂確認分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/payments/handlePaymentSuccess.ts:36</code> handlePaymentSuccess 簽名變更可能導致其他呼叫點未更新</summary>

`handlePaymentSuccess` 的參數從位置參數改為物件參數，但此 PR 僅更新了部分呼叫點（如 alby、btcpayserver、hitpay、paypal、stripe）。若專案中仍有其他未更新的呼叫點，將導致執行時錯誤。

建議：搜尋所有呼叫 `handlePaymentSuccess` 的位置，確認皆已更新。

**判斷依據**：diff 中 handlePaymentSuccess.ts 的函式簽名變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring 預訂的 acceptedBookings 可能包含非 PENDING 狀態的預訂</summary>

在 recurring 預訂確認時，`unconfirmedRecurringBookings` 是透過 `prisma.booking.findMany` 查詢 `status: BookingStatus.PENDING` 的預訂，因此 `acceptedBookings` 的 `oldStatus` 應為 `PENDING`。但程式碼直接使用 `booking.status`，若查詢條件正確，則無問題；但若未來條件變更，可能導致錯誤。建議明確設定 `oldStatus: BookingStatus.PENDING` 或保留查詢結果。

**判斷依據**：diff 中 handleConfirmation.ts 的 recurring 分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468</code> 單一預訂拒絕時 rejectedBookings 的 oldStatus 可能不正確</summary>

在非 recurring 的單一預訂拒絕流程中，`rejectedBookings` 被設定為 `[{ uid: booking.uid, oldStatus: booking.status }]`。但此處的 `booking` 是從資料庫取得的原始預訂，其狀態在拒絕前可能是 `PENDING` 或其他非 `REJECTED` 狀態。這會導致審計事件中的 `oldStatus` 錯誤。

建議：應使用更新前的實際狀態，例如從 `booking.status` 取得，或先查詢再更新。

**判斷依據**：diff 中 confirm.handler.ts 的單一預訂拒絕分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 schema 變更可能影響既有資料</summary>

`fieldsSchemaV1` 中的 `rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，且移除了 `previousReason` 欄位。這可能導致既有審計資料無法正確解析，或顯示時缺少先前原因。

建議：確認是否有既有資料需要遷移，或保留向後相容性。

**判斷依據**：diff 中 RejectedAuditActionService.ts 的 schema 定義變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 29972 (cache hit 29952) ｜ completion tokens 1421 ｜ PR #10</sub>