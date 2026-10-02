<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 booking audit 整合至確認/拒絕流程，新增 actor 與 actionSource 參數，並擴充測試。主要風險在於 `handleConfirmation` 中單筆接受時 `oldStatus` 被硬編碼為 `ACCEPTED`，可能導致 audit log 記錄錯誤；此外 `getAppActor` 對 `apps` 的型別處理可能不正確，且 `handlePaymentSuccess` 的簽名變更為破壞性，需確認所有呼叫點已更新。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆接受時 oldStatus 硬編碼為 ACCEPTED，可能記錄錯誤的 audit log | 0.90 |
| ⚠️ | Major | `packages/app-store/_utils/getAppActor.ts:32` | getAppActor 中 apps 參數型別可能不正確 | 0.80 |
| ⚠️ | Major | `packages/app-store/_utils/payments/handlePaymentSuccess.ts:36` | handlePaymentSuccess 簽名變更為破壞性，需確認所有呼叫點已更新 | 0.80 |
| ⚠️ | Major | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 fieldsSchemaV1 變更可能導致既有資料無法解析 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:263` | fireBookingAcceptedEvent 在 recurring 分支中可能使用錯誤的 oldStatus | 0.80 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/_router.tsx:62` | 缺少分號可能導致 ASI 問題 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆接受時 oldStatus 硬編碼為 ACCEPTED，可能記錄錯誤的 audit log</summary>

在 `handleConfirmation` 中，當 `recurringEventId` 不存在時，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 `PENDING` 或其他非 `ACCEPTED` 狀態，這會導致 audit log 中的 `oldStatus` 不正確。

建議從資料庫查詢 booking 的實際狀態，或使用先前已取得的 `booking.status`。

**判斷依據**：diff 中新增的程式碼片段，位於 `handleConfirmation` 函式內，在非 recurring 分支中。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/getAppActor.ts:32</code> getAppActor 中 apps 參數型別可能不正確</summary>

`getAppActor` 的參數 `apps` 型別為 `z.infer<typeof eventTypeAppMetadataOptionalSchema>`，但實際傳入的 `eventType?.metadata?.apps` 可能為 `null` 或 `undefined`。函式內使用 `apps?.[appSlug as keyof typeof apps]` 來存取，若 `apps` 為 `null` 或 `undefined`，此表達式會拋出錯誤。

建議先檢查 `apps` 是否存在，或將參數型別改為可選。

**判斷依據**：diff 中新增的 `getAppActor` 函式，第 31 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/payments/handlePaymentSuccess.ts:36</code> handlePaymentSuccess 簽名變更為破壞性，需確認所有呼叫點已更新</summary>

`handlePaymentSuccess` 的簽名從 `(paymentId, bookingId, traceContext)` 改為接受一個物件參數。此變更會影響所有呼叫此函式的地方，若未全部更新，將導致執行時錯誤。

請確認所有呼叫點（如其他 app store 的 webhook handler）都已更新。

**判斷依據**：diff 中 `handlePaymentSuccess.ts` 的函式簽名變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 fieldsSchemaV1 變更可能導致既有資料無法解析</summary>

`fieldsSchemaV1` 中的 `rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，且 `status` 改為 `BookingStatusChangeSchema`。這可能導致已儲存的 audit log 資料（使用舊 schema）在讀取時解析失敗。

需要確認是否有 migration 或相容性處理。

**判斷依據**：diff 中 `RejectedAuditActionService.ts` 的 schema 變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> fireBookingAcceptedEvent 在 recurring 分支中可能使用錯誤的 oldStatus</summary>

在 recurring 分支中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 取得，其 `oldStatus` 為 `booking.status`。但 `unconfirmedRecurringBookings` 查詢的條件是 `status: BookingStatus.PENDING`，因此 `oldStatus` 會是 `PENDING`，這可能是正確的。然而，若之後有其他狀態的 booking 被包含進來，則可能不正確。

建議確認查詢條件是否涵蓋所有需要更新的 booking。

**判斷依據**：diff 中 `handleConfirmation.ts` 的 recurring 分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/_router.tsx:62</code> 缺少分號可能導致 ASI 問題</summary>

在 `_router.tsx` 中，`input` 物件後缺少分號，雖然 JavaScript 的自動分號插入（ASI）通常會處理，但可能在某些情況下導致問題。

建議加上分號以保持一致。

**判斷依據**：diff 中 `_router.tsx` 的變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 30008 (cache hit 1536) ｜ completion tokens 1590 ｜ PR #10</sub>