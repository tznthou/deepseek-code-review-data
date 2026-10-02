<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 整合了 booking audit 功能，在多個入口（API v2、magic link、webhook、tRPC）加入 actor 與 actionSource，並新增 bulk rejected 事件處理與相關測試。主要風險在於 handleConfirmation 中 acceptedBookings 的 oldStatus 可能不正確、recurring 流程中 fireBookingAcceptedEvent 的時機與資料來源、以及 RejectedAuditActionService 的 schema 變更可能造成既有資料解析失敗。建議優先修正 acceptedBookings 的 oldStatus 來源，並確認 schema 變更的相容性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | acceptedBookings 的 oldStatus 固定為 ACCEPTED，導致 audit log 記錄錯誤 | 0.90 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring 流程中 fireBookingAcceptedEvent 在更新前呼叫，且 oldStatus 可能不準確 | 0.80 |
| ⚠️ | Major | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 schema 變更可能導致既有資料解析失敗 | 0.75 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/_router.tsx:62` | 缺少逗號可能導致語法錯誤 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:411` | 非 recurring 流程中 acceptedBookings 的 oldStatus 應從 booking 取得 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> acceptedBookings 的 oldStatus 固定為 ACCEPTED，導致 audit log 記錄錯誤</summary>

在非 recurring 的單一 booking 確認流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 PENDING（或甚至其他狀態），因為尚未執行更新。這會讓 audit log 中的 `status.old` 永遠是 ACCEPTED，而非實際的舊狀態。

**失敗情境**：當一個 PENDING booking 被確認時，audit log 會顯示 `{ old: ACCEPTED, new: ACCEPTED }`，失去稽核意義。

**建議**：在更新前先取得 booking 的原始狀態，例如從 `booking` 物件中讀取（如果已包含）或先查詢，然後使用該值作為 `oldStatus`。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation.ts 的 411 行附近。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring 流程中 fireBookingAcceptedEvent 在更新前呼叫，且 oldStatus 可能不準確</summary>

在 recurring 確認流程中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 取得，其 `oldStatus` 是 `booking.status`。但 `fireBookingAcceptedEvent` 是在 `prisma.booking.updateMany` 之前呼叫，因此 `oldStatus` 應為 PENDING（正確）。然而，`fireBookingAcceptedEvent` 內會呼叫 `getBookingEventHandlerService().onBulkBookingsAccepted`，這可能會觸發非同步的 audit 任務，而此時資料庫中的 booking 狀態尚未更新為 ACCEPTED。如果 audit 任務在更新前執行，可能會讀到舊狀態，導致 audit log 不一致。

**失敗情境**：audit 任務在 booking 更新前執行，記錄到 PENDING 而非 ACCEPTED。

**建議**：將 `fireBookingAcceptedEvent` 移到 `updateMany` 之後，並確保傳入的 `oldStatus` 是更新前的狀態。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation.ts 的 260 行附近。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 schema 變更可能導致既有資料解析失敗</summary>

`fieldsSchemaV1` 中的 `rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，且 `status` 改為 `BookingStatusChangeSchema`。這表示舊的 audit 資料（如果有）可能包含 `rejectionReason` 為 `{ old, new }` 的物件，現在會被 Zod 解析失敗，導致 `parseStored` 拋出錯誤。

**失敗情境**：如果資料庫中已有舊格式的 REJECTED audit 記錄，當使用者查看 audit log 時，`parseStored` 會拋出 ZodError，可能導致頁面錯誤。

**建議**：確認是否有舊資料需要遷移，或提供向後相容的 schema（例如 union 或 preprocess）。

**判斷依據**：diff 中 RejectedAuditActionService.ts 的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/_router.tsx:62</code> 缺少逗號可能導致語法錯誤</summary>

在 `_router.tsx` 中，`input` 物件的最後一個屬性 `actionSource: "WEBAPP"` 後面缺少逗號，這在 JavaScript/TypeScript 中會導致語法錯誤。

**失敗情境**：建置或執行時拋出 SyntaxError。

**建議**：在 `actionSource: "WEBAPP"` 後加上逗號。

**判斷依據**：diff 中 _router.tsx 的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 非 recurring 流程中 acceptedBookings 的 oldStatus 應從 booking 取得</summary>

在非 recurring 的單一 booking 確認流程中，`acceptedBookings` 的 `oldStatus` 被硬編碼為 `BookingStatus.ACCEPTED`，但實際上 booking 在更新前可能是其他狀態（如 PENDING）。這會導致 audit log 的 `status.old` 不正確。

**建議**：從 `booking` 物件中取得原始狀態，例如 `booking.status`（如果已包含在查詢中）。

**判斷依據**：diff 中 handleConfirmation.ts 的變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31447 (cache hit 1536) ｜ completion tokens 1836 ｜ PR #10</sub>