<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 booking audit 整合至確認/拒絕流程，新增 actor 與 actionSource 參數，並加入 MAGIC_LINK 來源。主要風險在於 handleConfirmation 中 acceptedBookings 的 oldStatus 可能不正確，以及 reject 流程中 rejectedBookings 的 oldStatus 在更新後才取得，導致 audit 記錄錯誤。另有少數型別與格式問題。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | acceptedBookings 的 oldStatus 在單一 booking 時硬編碼為 ACCEPTED，導致 audit 記錄錯誤 | 0.95 |
| 🛑 | Blocker | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432` | rejectedBookings 的 oldStatus 在更新後才取得，導致 audit 記錄錯誤 | 0.90 |
| ⚠️ | Major | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 fieldsSchemaV1 中 rejectionReason 型別從 StringChangeSchema 改為 z. | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | acceptedBookings 在非 recurring 分支中未考慮 booking 可能不存在或狀態非 PENDING 的情況 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:260` | fireBookingAcceptedEvent 在 recurring 分支中可能重複觸發 audit 事件 | 0.60 |
| 🔸 | Minor | `packages/app-store/_utils/getAppActor.ts:22` | getAppActor 函式缺少對 apps 參數的 null/undefined 檢查 | 0.50 |
| 🔸 | Minor | `packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:405` | queueBulkRejectedAudit 方法缺少 context 參數傳遞 | 0.50 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/_router.tsx:62` | confirm 路由中未處理 actor 或 actionSource 可能為 undefined 的情況 | 0.40 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> acceptedBookings 的 oldStatus 在單一 booking 時硬編碼為 ACCEPTED，導致 audit 記錄錯誤</summary>

在非 recurring 的確認流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的狀態尚未更新，實際舊狀態可能是 PENDING 或其他值。這會使 audit log 中的 `status.old` 永遠是 ACCEPTED，而非真正的舊狀態。

**失敗情境**：當一個 PENDING booking 被確認時，audit log 會記錄 `{ old: ACCEPTED, new: ACCEPTED }`，而不是 `{ old: PENDING, new: ACCEPTED }`。

**建議**：在更新前取得 booking 的舊狀態，例如從先前查詢的 `booking` 物件中取得 `booking.status`，並使用該值。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation 函式內，非 recurring 分支。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432</code> rejectedBookings 的 oldStatus 在更新後才取得，導致 audit 記錄錯誤</summary>

在 reject 流程中，程式碼先執行 `prisma.booking.updateMany` 將狀態改為 REJECTED，然後才查詢 `updatedRecurringBookings` 並將其 `status` 作為 `oldStatus`。這會使 `oldStatus` 永遠是 REJECTED，而非真正的舊狀態（例如 PENDING）。

**失敗情境**：當一個 PENDING booking 被拒絕時，audit log 會記錄 `{ old: REJECTED, new: REJECTED }`，而不是 `{ old: PENDING, new: REJECTED }`。

**建議**：在更新前先查詢並保存舊狀態，或使用 `unconfirmedRecurringBookings` 中的 `status` 作為 `oldStatus`。

**判斷依據**：diff 中新增的程式碼片段，位於 confirmHandler 的 reject 分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 fieldsSchemaV1 中 rejectionReason 型別從 StringChangeSchema 改為 z.string().nullable()，可能破壞既有資料相容性</summary>

原本 `rejectionReason` 使用 `StringChangeSchema`（包含 old/new 的變更記錄），現在改為單純的 `z.string().nullable()`。這會影響已儲存的 audit 資料：舊資料的 `rejectionReason` 是物件，新 schema 會解析失敗。

**失敗情境**：如果資料庫中已有舊格式的 REJECTED audit 記錄，當使用者查看 audit log 時，`parseStored` 會拋出 Zod 驗證錯誤，導致頁面無法顯示。

**建議**：保留 `StringChangeSchema` 或提供 migration 邏輯，將舊資料轉換為新格式。

**判斷依據**：diff 中 RejectedAuditActionService.ts 的變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> acceptedBookings 在非 recurring 分支中未考慮 booking 可能不存在或狀態非 PENDING 的情況</summary>

在非 recurring 分支中，`acceptedBookings` 被硬編碼為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`，但未檢查 `booking` 是否存在或狀態是否為 PENDING。如果 booking 不存在或狀態不是 PENDING，audit 記錄會不正確。

**失敗情境**：如果 booking 已被取消或不存在，程式碼仍會嘗試記錄 audit，可能導致錯誤或誤導。

**建議**：在設定 `acceptedBookings` 前，確認 booking 存在且狀態為 PENDING，否則跳過 audit 記錄。

**判斷依據**：diff 中新增的程式碼片段。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:260</code> fireBookingAcceptedEvent 在 recurring 分支中可能重複觸發 audit 事件</summary>

在 recurring 分支中，`fireBookingAcceptedEvent` 被呼叫，但之後在函式末尾又有一個 `if (!recurringEventId)` 的條件呼叫。這可能導致在 recurring 情況下 audit 事件被觸發兩次（一次在分支內，一次在分支外）。

**失敗情境**：如果 recurring 分支內的呼叫成功，且後續的 `if (!recurringEventId)` 條件判斷錯誤，可能導致重複記錄。

**建議**：確認邏輯，避免重複觸發。

**判斷依據**：diff 中新增的程式碼片段，位於 recurring 分支內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/app-store/_utils/getAppActor.ts:22</code> getAppActor 函式缺少對 apps 參數的 null/undefined 檢查</summary>

`getAppActor` 函式直接使用 `apps?.[appSlug as keyof typeof apps]`，但未檢查 `apps` 是否為 null 或 undefined。如果呼叫端傳入的 `apps` 為 null，會導致執行時錯誤。

**失敗情境**：如果 `eventType.metadata.apps` 為 null，`eventTypeAppMetadataOptionalSchema.parse` 可能回傳 null，傳入 `getAppActor` 後會拋出 TypeError。

**建議**：在函式開頭加入 `if (!apps) { ... }` 的處理，或確保呼叫端不會傳入 null。

**判斷依據**：diff 中新增的 getAppActor.ts 檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:405</code> queueBulkRejectedAudit 方法缺少 context 參數傳遞</summary>

`queueBulkRejectedAudit` 方法接收 `context` 參數，但在呼叫 `queueBulkTask` 時未將其傳入。這可能導致 context 資訊遺失。

**失敗情境**：如果 context 中包含重要的追蹤資訊，這些資訊將不會被傳遞到後續處理。

**建議**：將 `context` 加入 `queueBulkTask` 的參數中。

**判斷依據**：diff 中新增的 queueBulkRejectedAudit 方法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/_router.tsx:62</code> confirm 路由中未處理 actor 或 actionSource 可能為 undefined 的情況</summary>

在 `_router.tsx` 中，`confirmHandler` 被呼叫時傳入了 `actor: makeUserActor(ctx.user.uuid)` 和 `actionSource: "WEBAPP"`。但 `ctx.user.uuid` 可能為 undefined，導致 `makeUserActor` 收到 undefined。

**失敗情境**：如果使用者沒有 uuid，`makeUserActor` 可能拋出錯誤或產生不正確的 actor。

**建議**：確認 `ctx.user.uuid` 一定存在，或在 `makeUserActor` 中處理 undefined。

**判斷依據**：diff 中 _router.tsx 的變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31457 (cache hit 29952) ｜ completion tokens 2673 ｜ PR #10</sub>