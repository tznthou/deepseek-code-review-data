<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 整合了 booking audit 功能，在多個入口（API v2、magic link、webhook、tRPC）加入 actor 與 actionSource，並新增 bulk rejected 事件處理。主要風險在於 `handleConfirmation` 中單筆 booking 的 `oldStatus` 被硬編碼為 `ACCEPTED`，可能導致 audit log 記錄錯誤；此外 `confirmHandler` 的 reject 流程在更新後才取得狀態，造成 `oldStatus` 永遠是 `REJECTED`。另有 schema 變更（`rejectionReason` 從 change object 改為純字串）可能影響既有資料相容性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 oldStatus 硬編碼為 ACCEPTED，導致 audit log 錯誤 | 0.95 |
| 🛑 | Blocker | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468` | reject 流程中 oldStatus 取自更新後的 booking，導致 audit log 錯誤 | 0.90 |
| ⚠️ | Major | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:20` | rejectionReason schema 從 change object 改為純字串，可能破壞既有資料相容性 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring booking 的 oldStatus 可能不準確 | 0.75 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:413` | 非 recurring 分支中 acceptedBookings 的 oldStatus 應從 booking 物件取得 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 oldStatus 硬編碼為 ACCEPTED，導致 audit log 錯誤</summary>

在 `handleConfirmation` 的非 recurring 分支中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 尚未更新，其狀態可能是 `PENDING` 或其他非 `ACCEPTED` 狀態。這會導致 audit log 中的 `status.old` 永遠是 `ACCEPTED`，而非實際的舊狀態。

**失敗情境**：當一個 `PENDING` booking 被確認時，audit log 會記錄 `{ old: ACCEPTED, new: ACCEPTED }`，無法反映狀態變更。

**建議**：在更新前先取得 booking 的原始狀態，例如從 `booking` 物件中讀取 `booking.status`，並使用該值作為 `oldStatus`。

**判斷依據**：diff 中新增的 `acceptedBookings` 賦值，在 `handleConfirmation` 的非 recurring 分支，且未先讀取 `booking.status`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468</code> reject 流程中 oldStatus 取自更新後的 booking，導致 audit log 錯誤</summary>

在 `confirmHandler` 的 reject 分支中，`rejectedBookings` 的 `oldStatus` 是從 `booking.status` 取得，但此時 `booking` 物件已在前面被更新為 `REJECTED`（透過 `prisma.booking.update`）。因此 `oldStatus` 會是 `REJECTED`，而非更新前的狀態（例如 `PENDING`）。

**失敗情境**：當一個 `PENDING` booking 被拒絕時，audit log 會記錄 `{ old: REJECTED, new: REJECTED }`，無法反映狀態變更。

**建議**：在更新前先保存原始狀態，例如在更新前讀取 `booking.status` 並存入變數，再於更新後使用該變數。

**判斷依據**：diff 中 `rejectedBookings` 的賦值位於 `prisma.booking.update` 之後，且 `booking.status` 已被更新為 `REJECTED`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:20</code> rejectionReason schema 從 change object 改為純字串，可能破壞既有資料相容性</summary>

`fieldsSchemaV1` 中的 `rejectionReason` 從 `StringChangeSchema`（包含 `old` 和 `new` 的物件）改為 `z.string().nullable()`。這會導致已儲存的 audit log 資料（如果存在）無法通過新的 schema 驗證，因為它們的 `rejectionReason` 是物件而非字串。

**失敗情境**：如果系統中已有使用舊 schema 儲存的 audit log，當嘗試讀取或顯示這些記錄時，`parseStored` 會拋出 Zod 驗證錯誤。

**建議**：若需要變更 schema，應提供 migration 或向後相容的解析方式，例如保留 `StringChangeSchema` 或使用 union 型別。

**判斷依據**：diff 中 `rejectionReason` 的型別從 `StringChangeSchema` 改為 `z.string().nullable()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring booking 的 oldStatus 可能不準確</summary>

在 recurring 分支中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 映射而來，使用 `booking.status` 作為 `oldStatus`。但 `unconfirmedRecurringBookings` 是在更新前查詢的，因此其 `status` 應為 `PENDING`（因為查詢條件是 `status: BookingStatus.PENDING`）。這部分看起來正確，但需確認查詢條件是否涵蓋所有應更新的 booking。

**失敗情境**：如果某些 booking 的狀態不是 `PENDING` 但仍需更新（例如 `ACCEPTED` 但需要重新確認），則不會被包含在 `unconfirmedRecurringBookings` 中，導致 audit log 遺漏。

**建議**：確認查詢條件是否正確，或考慮使用更廣泛的條件並在更新前記錄狀態。

**判斷依據**：diff 中 `acceptedBookings` 的映射，依賴於 `unconfirmedRecurringBookings` 的查詢條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:413</code> 非 recurring 分支中 acceptedBookings 的 oldStatus 應從 booking 物件取得</summary>

與第一個 finding 相關，但此處強調程式碼可讀性：直接使用 `booking.status` 會比硬編碼 `BookingStatus.ACCEPTED` 更清晰且不易出錯。

**判斷依據**：diff 中該行位於 `acceptedBookings` 陣列內。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31447 (cache hit 31360) ｜ completion tokens 1712 ｜ PR #10</sub>