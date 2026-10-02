<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 booking audit 整合至確認/拒絕流程，新增 MAGIC_LINK 來源、actor 傳遞與 bulk rejected 事件。主要風險在於 handleConfirmation 中單筆 booking 的 acceptedBookings 狀態固定為 ACCEPTED，可能導致 audit 記錄不正確；此外部分測試的 mock 設定可能不完整，且新增的 getAppActor 在缺少 credentialId 時僅記錄警告，可能影響後續稽核。建議先修正 acceptedBookings 的狀態來源，並確認測試覆蓋。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 acceptedBookings 狀態固定為 ACCEPTED，可能導致 audit 記錄不正確 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring 確認時 acceptedBookings 的 oldStatus 可能不準確 | 0.70 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:444` | recurring 拒絕時 rejectedBookings 的 oldStatus 可能不正確 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:249` | acceptedBookings 變數宣告後未初始化，可能導致未定義錯誤 | 0.60 |
| 🔸 | Minor | `packages/app-store/_utils/getAppActor.ts:36` | 缺少 credentialId 時僅記錄警告，可能導致 audit 記錄不完整 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:434` | 非 recurring 的 fireBookingAcceptedEvent 呼叫位置可能導致重複觸發 | 0.50 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468` | 單筆拒絕時 rejectedBookings 的 oldStatus 可能不正確 | 0.50 |
| 🔸 | Minor | `packages/app-store/_utils/payments/handlePaymentSuccess.ts:49` | eventType.metadata.apps 可能為 undefined，導致 parse 失敗 | 0.50 |
| 🔸 | Minor | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:20` | rejectionReason 型別從 StringChangeSchema 改為 z.string().nullable()，可能影響既有資料相容性 | 0.50 |
| 🔸 | Minor | `packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:415` | queueBulkRejectedAudit 方法缺少 context 參數傳遞 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 acceptedBookings 狀態固定為 ACCEPTED，可能導致 audit 記錄不正確</summary>

在非 recurring 的確認流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能不是 ACCEPTED（例如 PENDING），這會導致 audit 記錄中的 `oldStatus` 錯誤。應改為使用 booking 更新前的實際狀態。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation.ts 的 411 行附近，將 oldStatus 硬編碼為 BookingStatus.ACCEPTED。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring 確認時 acceptedBookings 的 oldStatus 可能不準確</summary>

在 recurring 確認流程中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 取得，但該查詢只選取 `uid` 和 `status`，且 `status` 是查詢當下的值。然而後續 `updateMany` 會將狀態改為 ACCEPTED，但 `acceptedBookings` 的 `oldStatus` 仍是更新前的值，這部分正確。但需確認 `unconfirmedRecurringBookings` 的查詢條件是否包含所有應更新的 bookings（例如 status 為 PENDING 的），否則可能漏掉部分 bookings。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation.ts 的 260 行附近。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:444</code> recurring 拒絕時 rejectedBookings 的 oldStatus 可能不正確</summary>

在 recurring 拒絕流程中，先查詢 `unconfirmedRecurringBookings` 取得 uid 和 status，然後執行 `updateMany` 將狀態改為 REJECTED，接著再次查詢 `updatedRecurringBookings` 取得更新後的 status，並將其作為 `oldStatus` 放入 `rejectedBookings`。這會導致 audit 記錄中的 oldStatus 是 REJECTED 而不是更新前的 PENDING。應使用第一次查詢的 status 作為 oldStatus。

**判斷依據**：diff 中新增的程式碼片段，位於 confirm.handler.ts 的 393 行附近。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:249</code> acceptedBookings 變數宣告後未初始化，可能導致未定義錯誤</summary>

`let acceptedBookings: { oldStatus: BookingStatus; uid: string; }[];` 宣告後未初始化，雖然在後續的 if/else 分支中都會賦值，但若未來程式碼變更導致某個路徑未賦值，則在 `fireBookingAcceptedEvent` 中使用時會出錯。建議初始化為空陣列。

**判斷依據**：diff 中新增的變數宣告，位於 handleConfirmation.ts 的 246 行附近。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/app-store/_utils/getAppActor.ts:36</code> 缺少 credentialId 時僅記錄警告，可能導致 audit 記錄不完整</summary>

當 app 沒有 credentialId 時，`getAppActor` 會使用 appSlug 建立 actor，但僅記錄警告。這可能導致 audit 記錄中的 actor 資訊不完整，影響後續稽核。建議考慮是否應拋出錯誤或提供更明確的處理方式。

**判斷依據**：diff 中新增的程式碼片段，位於 getAppActor.ts 的 37 行附近。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:434</code> 非 recurring 的 fireBookingAcceptedEvent 呼叫位置可能導致重複觸發</summary>

在非 recurring 的確認流程中，`fireBookingAcceptedEvent` 被呼叫在 `updatedBookings.push(updatedBooking)` 之後，但 `updatedBooking` 的狀態可能已經是 ACCEPTED，而 `acceptedBookings` 的 oldStatus 被硬編碼為 ACCEPTED，這可能導致 audit 記錄的 oldStatus 和 newStatus 相同，失去意義。建議確認此處的邏輯。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation.ts 的 431 行附近。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468</code> 單筆拒絕時 rejectedBookings 的 oldStatus 可能不正確</summary>

在單筆拒絕流程中，`rejectedBookings` 被設定為 `[{ uid: booking.uid, oldStatus: booking.status }]`，但此時 `booking.status` 可能已經是 REJECTED（因為前面已經執行 `prisma.booking.update` 將狀態改為 REJECTED）。應在更新前保存舊狀態。

**判斷依據**：diff 中新增的程式碼片段，位於 confirm.handler.ts 的 464 行附近。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/app-store/_utils/payments/handlePaymentSuccess.ts:49</code> eventType.metadata.apps 可能為 undefined，導致 parse 失敗</summary>

`eventTypeAppMetadataOptionalSchema.parse(eventType?.metadata?.apps)` 中，若 `eventType.metadata` 或 `eventType.metadata.apps` 為 undefined，parse 可能拋出錯誤。建議使用 optional 處理或提供預設值。

**判斷依據**：diff 中新增的程式碼片段，位於 handlePaymentSuccess.ts 的 44 行附近。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:20</code> rejectionReason 型別從 StringChangeSchema 改為 z.string().nullable()，可能影響既有資料相容性</summary>

原本 `rejectionReason` 使用 `StringChangeSchema`（包含 old/new），現在改為 `z.string().nullable()`，這可能導致已儲存的 audit 資料無法正確解析。需確認是否有 migration 或相容性處理。

**判斷依據**：diff 中修改的 schema 定義，位於 RejectedAuditActionService.ts 的 28 行附近。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:415</code> queueBulkRejectedAudit 方法缺少 context 參數傳遞</summary>

`queueBulkRejectedAudit` 方法中呼叫 `queueBulkTask` 時未傳遞 `context`，但介面定義中包含 `context?: BookingAuditContext`。這可能導致 context 資訊遺失。

**判斷依據**：diff 中新增的方法，位於 BookingAuditTaskerProducerService.ts 的 404 行附近。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31447 (cache hit 29952) ｜ completion tokens 2493 ｜ PR #10</sub>