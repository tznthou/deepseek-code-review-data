<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 booking audit 整合至確認/拒絕流程，新增 actor 與 actionSource 參數，並擴充測試。主要風險在於 handleConfirmation 中 acceptedBookings 的 oldStatus 可能不正確（單筆時硬編碼為 ACCEPTED），以及 RejectedAuditActionService 的 schema 變更可能造成既有資料解析失敗。建議先修正這兩個問題再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆確認時 acceptedBookings 的 oldStatus 硬編碼為 ACCEPTED，導致 audit log 狀態變更不正確 | 0.90 |
| ⚠️ | Major | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 fieldsSchemaV1 變更可能造成既有資料解析失敗 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring 確認時 acceptedBookings 的 oldStatus 可能不正確 | 0.75 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468` | 單筆拒絕時 rejectedBookings 的 oldStatus 可能不正確 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:249` | acceptedBookings 變數可能未初始化 | 0.60 |
| 🔸 | Minor | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:47` | getDisplayJson 中移除了 previousReason 欄位 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆確認時 acceptedBookings 的 oldStatus 硬編碼為 ACCEPTED，導致 audit log 狀態變更不正確</summary>

在非 recurring 的分支中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 PENDING（或甚至其他狀態），因此 audit log 會記錄錯誤的狀態變更（例如 PENDING → ACCEPTED 被記錄成 ACCEPTED → ACCEPTED）。

**失敗情境**：當一個 PENDING booking 被確認時，audit log 會顯示 previousStatus 為 ACCEPTED，而非 PENDING，造成稽核資料錯誤。

**建議**：從 `booking` 物件取得實際的舊狀態，例如 `oldStatus: booking.status`。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation 的非 recurring 分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 fieldsSchemaV1 變更可能造成既有資料解析失敗</summary>

原本 `rejectionReason` 使用 `StringChangeSchema`（具有 old/new 結構），現在改為 `z.string().nullable()`。這會導致已儲存的 audit log 資料（包含 `{ old, new }` 物件）在 `parseStored` 時驗證失敗，因為 schema 不再接受物件。

**失敗情境**：升級後，任何讀取舊的 REJECTED audit log 的操作都會拋出 Zod 驗證錯誤，可能導致頁面無法顯示歷史紀錄。

**建議**：保留舊 schema 作為 stored schema，並在 migrateToLatest 中處理轉換，或使用 union 型別相容新舊格式。

**判斷依據**：diff 中將 `rejectionReason: StringChangeSchema` 改為 `rejectionReason: z.string().nullable()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring 確認時 acceptedBookings 的 oldStatus 可能不正確</summary>

在 recurring 分支中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 取得，但該查詢的 `where` 條件是 `status: BookingStatus.PENDING`，因此 `oldStatus` 會是 PENDING。然而，在後續的 `updateMany` 之後，這些 booking 的狀態已變為 ACCEPTED，但 `acceptedBookings` 仍保留舊的 PENDING 狀態，這在 audit log 中是正確的。但需注意，如果 `unconfirmedRecurringBookings` 包含非 PENDING 的 booking（例如查詢條件有誤），則 oldStatus 會不正確。

**失敗情境**：如果查詢條件未正確過濾，可能包含已 ACCEPTED 的 booking，導致 audit log 記錄 ACCEPTED → ACCEPTED。

**建議**：確認查詢條件正確，或直接從 `unconfirmedRecurringBookings` 取得狀態，並確保其為 PENDING。

**判斷依據**：diff 中新增的程式碼片段，位於 recurring 分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468</code> 單筆拒絕時 rejectedBookings 的 oldStatus 可能不正確</summary>

在非 recurring 的拒絕分支中，`rejectedBookings` 被設定為 `[{ uid: booking.uid, oldStatus: booking.status }]`。但 `booking.status` 是在 `prisma.booking.update` 之前取得的，因此是舊狀態（PENDING），這在 audit log 中是正確的。然而，如果 `booking.status` 不是 PENDING（例如已 ACCEPTED），則 audit log 會記錄錯誤的狀態變更。

**失敗情境**：如果 booking 在拒絕前已被其他流程更改狀態，audit log 會顯示不正確的 previousStatus。

**建議**：確認 booking 在拒絕前一定是 PENDING，或從資料庫重新取得狀態。

**判斷依據**：diff 中新增的程式碼片段，位於非 recurring 拒絕分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:249</code> acceptedBookings 變數可能未初始化</summary>

`acceptedBookings` 在宣告時未初始化，僅在 `recurringEventId` 或非 recurring 分支中賦值。如果未來程式碼路徑未涵蓋所有情況，可能導致 `undefined` 傳入 `fireBookingAcceptedEvent`。

**失敗情境**：如果新增其他分支而未設定 `acceptedBookings`，則會傳入 undefined，可能導致錯誤。

**建議**：初始化為空陣列，或確保所有路徑都賦值。

**判斷依據**：diff 中新增的變數宣告，未初始化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:47</code> getDisplayJson 中移除了 previousReason 欄位</summary>

原本 `getDisplayJson` 回傳 `previousReason`，現在被移除。這可能影響前端顯示，如果前端仍依賴此欄位，會導致 undefined。

**失敗情境**：前端嘗試顯示 previousReason 時會得到 undefined，可能顯示錯誤或空白。

**建議**：確認前端已更新，或保留 previousReason 欄位以相容。

**判斷依據**：diff 中移除了 `previousReason: fields.rejectionReason.old ?? null`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31437 (cache hit 29952) ｜ completion tokens 1906 ｜ PR #10</sub>