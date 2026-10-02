<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 將 booking audit 整合到確認/拒絕流程中，新增了 actor 與 actionSource 參數，並在付款成功與 magic link 等路徑中傳遞。主要風險在於 `handleConfirmation` 中單筆 booking 的 `oldStatus` 被硬編碼為 `ACCEPTED`，可能導致 audit log 記錄錯誤；此外 `handlePaymentSuccess` 的簽名變更為物件參數，但部分呼叫點可能未同步更新，需確認所有呼叫點都已修正。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED | 0.90 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring bookings 的 oldStatus 可能不正確 | 0.85 |
| ⚠️ | Major | `packages/app-store/_utils/payments/handlePaymentSuccess.ts:36` | handlePaymentSuccess 簽名變更可能導致其他呼叫點未更新 | 0.80 |
| 🔸 | Minor | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 schema 變更可能影響既有資料 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 oldStatus 硬編碼可能導致測試覆蓋不足 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED</summary>

在 `handleConfirmation` 中，當 `recurringEventId` 不存在時，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 `PENDING` 或其他非 `ACCEPTED` 狀態，這會導致 audit log 中的 `oldStatus` 不正確。

**失敗情境**：當一個 pending booking 被確認時，audit log 會記錄 `oldStatus: ACCEPTED` 而不是 `PENDING`，造成資料錯誤。

**建議**：從資料庫中取得 booking 的實際狀態，例如在更新前先查詢 `booking.status`，並使用該值作為 `oldStatus`。

**判斷依據**：diff 中新增的程式碼片段，位於 `handleConfirmation` 函式內，在 `recurringEventId` 為 falsy 的分支中。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring bookings 的 oldStatus 可能不正確</summary>

在處理 recurring bookings 時，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 映射而來，其 `oldStatus` 取自 `booking.status`。然而，在呼叫 `fireBookingAcceptedEvent` 之前，這些 bookings 尚未被更新，因此 `oldStatus` 應為 `PENDING`。但若 `unconfirmedRecurringBookings` 查詢的條件是 `status: BookingStatus.PENDING`，則 `oldStatus` 會是 `PENDING`，這部分正確。但需確認查詢條件是否包含其他狀態，例如 `ACCEPTED` 但尚未確認的 bookings。

**失敗情境**：如果查詢條件包含了非 `PENDING` 的 bookings，則 `oldStatus` 可能不正確。

**建議**：確認查詢條件僅包含 `PENDING` 狀態，或明確指定 `oldStatus` 為 `PENDING`。

**判斷依據**：diff 中新增的程式碼片段，位於 `handleConfirmation` 函式內，處理 recurring bookings 的分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/payments/handlePaymentSuccess.ts:36</code> handlePaymentSuccess 簽名變更可能導致其他呼叫點未更新</summary>

`handlePaymentSuccess` 的簽名從 `(paymentId, bookingId, traceContext)` 改為接受一個物件參數。雖然 diff 中更新了幾個呼叫點（如 alby、btcpayserver、hitpay、paypal、stripe），但可能還有其他未在 diff 中出現的呼叫點未更新，導致執行時錯誤。

**失敗情境**：如果有其他檔案仍以舊的參數形式呼叫 `handlePaymentSuccess`，會因為參數不匹配而拋出錯誤。

**建議**：全域搜尋 `handlePaymentSuccess(` 並確認所有呼叫點都已更新為新的物件參數形式。

**判斷依據**：diff 中 `handlePaymentSuccess.ts` 的函式簽名變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 schema 變更可能影響既有資料</summary>

`fieldsSchemaV1` 中的 `rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，這表示不再追蹤 rejectionReason 的變更（old/new），而只記錄最終值。這可能影響既有 audit log 的顯示或遷移邏輯。

**失敗情境**：如果既有資料中 `rejectionReason` 是以 `{ old, new }` 格式儲存，新的 schema 解析會失敗。

**建議**：確認資料庫中既有資料的格式，並提供遷移或相容性處理。

**判斷依據**：diff 中 `RejectedAuditActionService.ts` 的 schema 定義變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 oldStatus 硬編碼可能導致測試覆蓋不足</summary>

在測試中，可能沒有覆蓋到單筆 booking 確認時 `oldStatus` 不為 `ACCEPTED` 的情境，導致此錯誤未被發現。

**建議**：新增測試案例，驗證當 booking 狀態為 `PENDING` 時，audit log 的 `oldStatus` 為 `PENDING`。

**判斷依據**：diff 中新增的程式碼片段，且測試檔案中未見相關測試。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 30008 (cache hit 29952) ｜ completion tokens 1653 ｜ PR #10</sub>