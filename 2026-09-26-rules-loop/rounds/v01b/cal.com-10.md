<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 booking audit 整合至確認/拒絕流程，新增 actor 與 actionSource 參數，並擴充測試。主要風險在於 reject 流程中 oldStatus 的取得時機錯誤，可能導致 audit log 記錄不正確；此外 handleConfirmation 中 acceptedBookings 的 oldStatus 硬編碼為 ACCEPTED，與實際狀態不符。建議修正後再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468` | reject 流程中 oldStatus 取得時機錯誤，導致 audit log 記錄不正確 | 0.95 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | acceptedBookings 的 oldStatus 硬編碼為 ACCEPTED，可能與實際狀態不符 | 0.85 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432` | recurring reject 流程中 oldStatus 取得時機錯誤 | 0.80 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring 確認流程中 acceptedBookings 的 oldStatus 可能不正確 | 0.70 |
| 🔸 | Minor | `packages/app-store/_utils/getAppActor.ts:33` | getAppActor 中 credentialId 可能為 0 或空字串，導致 fallback 邏輯失效 | 0.60 |
| 🔸 | Minor | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 fieldsSchemaV1 中 rejectionReason 改為 z.string().nullable()，可能與 | 0.60 |
| 🔸 | Minor | `packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:405` | queueBulkRejectedAudit 方法缺少 context 參數傳遞 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468</code> reject 流程中 oldStatus 取得時機錯誤，導致 audit log 記錄不正確</summary>

在 `else` 分支（非 recurring）中，`rejectedBookings` 的 `oldStatus` 取自 `booking.status`，但此時 `booking` 物件尚未更新，其 `status` 仍為 `PENDING`。然而，在 `prisma.booking.update` 之後才設定 `rejectedBookings`，因此 `oldStatus` 會是 `PENDING`，但實際上更新前的狀態可能不是 `PENDING`（例如 `ACCEPTED`）。這會導致 audit log 中的 `oldStatus` 錯誤。

建議在更新前先取得 `booking.status`，或直接使用 `booking.status` 作為 `oldStatus`，並在更新後再設定 `rejectedBookings`。

**判斷依據**：diff 中新增的 `rejectedBookings` 設定位於 `prisma.booking.update` 之後，但 `booking.status` 在更新前並未被保存，因此 `oldStatus` 會是更新前的狀態，而非更新後的狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> acceptedBookings 的 oldStatus 硬編碼為 ACCEPTED，可能與實際狀態不符</summary>

在非 recurring 的確認流程中，`acceptedBookings` 的 `oldStatus` 被硬編碼為 `BookingStatus.ACCEPTED`，但實際上更新前的狀態可能是 `PENDING` 或其他狀態。這會導致 audit log 中的 `oldStatus` 不正確。

建議在更新前取得 booking 的實際狀態，並使用該狀態作為 `oldStatus`。

**判斷依據**：diff 中新增的 `acceptedBookings` 設定直接使用 `BookingStatus.ACCEPTED` 作為 `oldStatus`，但未從資料庫取得實際狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432</code> recurring reject 流程中 oldStatus 取得時機錯誤</summary>

在 recurring 的 reject 流程中，先執行 `prisma.booking.updateMany` 將所有符合條件的 booking 更新為 `REJECTED`，然後再查詢這些 booking 並取得其 `status` 作為 `oldStatus`。但此時 `status` 已經是 `REJECTED`，因此 `oldStatus` 會是 `REJECTED`，而非更新前的狀態。

建議在更新前先查詢並保存原始狀態，或使用 `unconfirmedRecurringBookings` 中的 `status` 作為 `oldStatus`。

**判斷依據**：diff 中新增的 `updatedRecurringBookings` 查詢發生在 `updateMany` 之後，因此取得的 `status` 已是更新後的值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring 確認流程中 acceptedBookings 的 oldStatus 可能不正確</summary>

在 recurring 的確認流程中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 映射而來，其 `oldStatus` 取自 `booking.status`。但 `unconfirmedRecurringBookings` 是在更新前查詢的，因此 `status` 應為 `PENDING`，這部分正確。然而，若後續更新失敗，audit log 可能已記錄，但實際狀態未變更。建議考慮將 audit 事件的發送與資料庫更新放在同一交易中，或至少確保更新成功後再發送事件。

**判斷依據**：diff 中新增的 `acceptedBookings` 設定在 `updateMany` 之前，但未考慮更新失敗的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/app-store/_utils/getAppActor.ts:33</code> getAppActor 中 credentialId 可能為 0 或空字串，導致 fallback 邏輯失效</summary>

在 `getAppActor` 中，使用 `if (appData?.credentialId)` 來判斷是否有 credentialId。若 `credentialId` 為 0 或空字串，條件為 false，會進入 fallback 分支，但實際上可能是有 credentialId 的。建議使用更嚴格的檢查，例如 `if (appData?.credentialId !== undefined && appData?.credentialId !== null)`。

**判斷依據**：diff 中新增的 `getAppActor` 函式使用 truthy 檢查，可能無法正確處理 0 或空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 fieldsSchemaV1 中 rejectionReason 改為 z.string().nullable()，可能與既有資料不相容</summary>

原本的 `rejectionReason` 使用 `StringChangeSchema`（包含 old/new），現在改為 `z.string().nullable()`。這可能導致既有 audit log 資料無法正確解析，因為舊資料的 `rejectionReason` 是物件而非字串。建議確認是否有 migration 或相容性處理。

**判斷依據**：diff 中將 `rejectionReason` 的 schema 從 `StringChangeSchema` 改為 `z.string().nullable()`，但未提供 migration。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:405</code> queueBulkRejectedAudit 方法缺少 context 參數傳遞</summary>

`queueBulkRejectedAudit` 方法接收 `context` 參數，但在呼叫 `queueBulkTask` 時未傳遞 `context`。這可能導致 context 資訊遺失。建議確認 `queueBulkTask` 是否需要 context，並補上。

**判斷依據**：diff 中新增的 `queueBulkRejectedAudit` 方法未將 `context` 傳遞給 `queueBulkTask`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31447 (cache hit 31360) ｜ completion tokens 2215 ｜ PR #10</sub>