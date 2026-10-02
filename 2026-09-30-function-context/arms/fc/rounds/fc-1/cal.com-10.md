<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 booking audit 整合至確認/拒絕流程，新增 MAGIC_LINK 來源與 app actor 支援。主要風險在於 handleConfirmation 中單筆 booking 的 acceptedBookings 使用硬編碼的 ACCEPTED 作為舊狀態，可能導致 audit log 不正確；此外，部分程式碼在 production 環境會跳過 audit queue，需確認是否為預期行為。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 acceptedBookings 舊狀態硬編碼為 ACCEPTED | 0.90 |
| ⚠️ | Major | `packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:85` | production 環境跳過 audit queue，可能導致 audit 遺失 | 0.85 |
| 🔸 | Minor | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:20` | RejectedAuditActionService 的 rejectionReason 型別變更可能影響既有資料 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:434` | acceptedBookings 在 recurring 與非 recurring 流程中可能重複觸發事件 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 acceptedBookings 舊狀態硬編碼為 ACCEPTED</summary>

在非 recurring 的單筆 booking 確認流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 尚未更新，其狀態應為 PENDING（或先前的狀態）。這會導致 audit log 中的 `status.old` 永遠是 ACCEPTED，而非實際的舊狀態，造成 audit 資料不正確。

建議：在更新前先取得 booking 的舊狀態，例如從 `booking.status` 取得，並使用該值。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation 的 else 分支，在 prisma.booking.update 之後。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:85</code> production 環境跳過 audit queue，可能導致 audit 遺失</summary>

在 `queueTask` 和 `queueBulkTask` 中，有 `if (IS_PRODUCTION) { return; }` 的判斷，這會導致在 production 環境下所有 audit 事件都不會被 queue，audit log 將完全缺失。若這是為了避免 production 負載而暫時停用，應有明確的 feature flag 或設定，而非直接 return。

建議：移除或改用 feature flag 控制，並確保 production 環境能正確記錄 audit。

**判斷依據**：diff 中新增的程式碼片段，位於 queueTask 和 queueBulkTask 方法內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:20</code> RejectedAuditActionService 的 rejectionReason 型別變更可能影響既有資料</summary>

`rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，這表示不再記錄舊的 rejection reason。若既有 audit log 中有舊格式的資料，解析時可能會失敗。需要確認是否有 migration 或相容性處理。

**判斷依據**：diff 中 RejectedAuditActionService.ts 的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:434</code> acceptedBookings 在 recurring 與非 recurring 流程中可能重複觸發事件</summary>

在 recurring 流程中，`fireBookingAcceptedEvent` 在更新前被呼叫；在非 recurring 流程中，則在更新後被呼叫。但非 recurring 流程中，`acceptedBookings` 的設定在 `fireBookingAcceptedEvent` 之前，且使用硬編碼的 ACCEPTED，可能導致事件觸發時機不一致。建議統一事件觸發的時機與資料來源。

**判斷依據**：diff 中 handleConfirmation.ts 的相關程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 59221 (cache hit 1536) ｜ completion tokens 1086 ｜ PR #10</sub>