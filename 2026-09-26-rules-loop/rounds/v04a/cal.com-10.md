<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 booking audit 功能整合至確認/拒絕流程，新增 actor 與 actionSource 參數，並加入 MAGIC_LINK 來源。整體方向合理，但存在幾個需要修正的問題：最嚴重的是 `handleConfirmation` 中單筆 booking 的 `oldStatus` 被硬編碼為 `ACCEPTED`，可能導致 audit log 記錄錯誤；其次是 `handlePaymentSuccess` 的函式簽章變更未同步更新所有呼叫點，可能造成執行時期錯誤；另有測試中 mock 未正確設定、型別不一致等問題。建議先修正上述 blocker 與 major 問題後再合併。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED，導致 audit log 記錄錯誤 | 0.95 |
| 🛑 | Blocker | `packages/app-store/_utils/payments/handlePaymentSuccess.ts:36` | handlePaymentSuccess 函式簽章變更，但部分呼叫點未同步更新 | 0.90 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:253` | fireBookingAcceptedEvent 在 recurring 分支中可能重複觸發事件 | 0.80 |
| ⚠️ | Major | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 fieldsSchemaV1 中 rejectionReason 型別從 StringChangeSchema 改為 z. | 0.75 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 acceptedBookings 陣列在非 recurring 分支中未正確初始化 | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/_router.tsx:18` | 在 _router.tsx 中直接呼叫 makeUserActor，可能違反 R02（防止核心套件間的循環依賴） | 0.60 |
| 🔸 | Minor | `packages/app-store/_utils/payments/handlePaymentSuccess.ts:36` | handlePaymentSuccess 的參數物件缺少明確的型別匯出，可能影響其他模組的使用 | 0.50 |
| 🔸 | Minor | `packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:405` | queueBulkRejectedAudit 方法缺少 context 參數的傳遞 | 0.40 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED，導致 audit log 記錄錯誤</summary>

在 `handleConfirmation` 中，當處理單筆 booking（非 recurring）時，`acceptedBookings` 陣列的 `oldStatus` 被直接設定為 `BookingStatus.ACCEPTED`，但實際上 booking 在確認前的狀態可能是 `PENDING` 或其他狀態。這會導致 audit log 中的狀態變更記錄不正確。

**失敗情境**：一個狀態為 `PENDING` 的 booking 被確認後，audit log 會記錄 `{ old: ACCEPTED, new: ACCEPTED }`，而非 `{ old: PENDING, new: ACCEPTED }`。

**建議修法**：從 `booking` 物件取得實際的舊狀態，例如 `oldStatus: booking.status`。

**判斷依據**：diff 中新增的程式碼片段：
```
+    acceptedBookings = [
+      {
+        oldStatus: BookingStatus.ACCEPTED,
+        uid: booking.uid,
+      },
+    ];
```
此處將 `oldStatus` 固定為 `BookingStatus.ACCEPTED`，但 `booking` 物件在確認前應有其他狀態。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/app-store/_utils/payments/handlePaymentSuccess.ts:36</code> handlePaymentSuccess 函式簽章變更，但部分呼叫點未同步更新</summary>

`handlePaymentSuccess` 的簽章從 `(paymentId, bookingId, traceContext)` 改為接受一個物件參數 `{ paymentId, appSlug, bookingId, traceContext }`。然而，在 `packages/features/ee/payments/api/webhook.ts` 中的呼叫點可能未完全更新，導致執行時期錯誤。

**失敗情境**：當 Stripe webhook 觸發時，呼叫 `handlePaymentSuccess(payment.id, payment.bookingId, traceContext)` 會因為參數型別不符而拋出錯誤。

**建議修法**：搜尋所有 `handlePaymentSuccess` 的呼叫點，確保皆已更新為新的物件參數形式。

**判斷依據**：diff 中 `handlePaymentSuccess` 的簽章已變更，但未看到所有呼叫點（例如 `packages/features/ee/payments/api/webhook.ts`）的對應修改。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:253</code> fireBookingAcceptedEvent 在 recurring 分支中可能重複觸發事件</summary>

在 `handleConfirmation` 中，當 `recurringEventId` 存在時，程式碼會先呼叫 `fireBookingAcceptedEvent`，然後在後續的 `if (!recurringEventId)` 區塊中又呼叫一次。這可能導致 audit 事件被重複記錄。

**失敗情境**：一個 recurring booking 被確認時，`fireBookingAcceptedEvent` 會被呼叫兩次，產生重複的 audit log。

**建議修法**：確認邏輯，避免重複呼叫。

**判斷依據**：diff 中顯示 `fireBookingAcceptedEvent` 在 `if (recurringEventId)` 和 `if (!recurringEventId)` 兩個分支中都被呼叫，但這兩個分支是互斥的，因此實際上只會呼叫一次。然而，程式碼結構可能造成誤解，建議重構以明確表達意圖。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 fieldsSchemaV1 中 rejectionReason 型別從 StringChangeSchema 改為 z.string().nullable()，可能破壞既有資料相容性</summary>

原本 `rejectionReason` 使用 `StringChangeSchema`（包含 old/new 欄位），現在改為單純的 `z.string().nullable()`。這會影響已儲存的 audit log 資料，因為舊資料的 `rejectionReason` 是物件，新 schema 無法解析。

**失敗情境**：當讀取舊的 audit log 時，`parseStored` 會因為 `rejectionReason` 型別不符而拋出錯誤。

**建議修法**：若需要變更 schema，應提供 migration 或保留向後相容的解析邏輯。

**判斷依據**：diff 中將 `rejectionReason: StringChangeSchema` 改為 `rejectionReason: z.string().nullable()`，但未見對應的 migration 或相容處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 acceptedBookings 陣列在非 recurring 分支中未正確初始化</summary>

在 `handleConfirmation` 中，`acceptedBookings` 變數在 `recurringEventId` 分支中被賦值，但在非 recurring 分支中，它被重新賦值為一個只有一個元素的陣列，且 `oldStatus` 被硬編碼為 `ACCEPTED`。這可能導致 audit log 記錄錯誤。

**失敗情境**：一個狀態為 `PENDING` 的 booking 被確認後，audit log 會記錄 `{ old: ACCEPTED, new: ACCEPTED }`。

**建議修法**：從 `booking` 物件取得實際的舊狀態。

**判斷依據**：diff 中新增的程式碼片段，`oldStatus` 被硬編碼為 `BookingStatus.ACCEPTED`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/_router.tsx:18</code> 在 _router.tsx 中直接呼叫 makeUserActor，可能違反 R02（防止核心套件間的循環依賴）</summary>

`_router.tsx` 位於 `packages/trpc`，而 `makeUserActor` 位於 `packages/features/booking-audit`。根據規範 R02，應避免核心套件之間的循環依賴。雖然目前可能沒有循環，但直接從 trpc 匯入 features 套件可能增加耦合。

**建議修法**：考慮將 actor 的建立邏輯移至更合適的層級，或透過依賴注入。

**判斷依據**：diff 中新增的 import 陳述式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/app-store/_utils/payments/handlePaymentSuccess.ts:36</code> handlePaymentSuccess 的參數物件缺少明確的型別匯出，可能影響其他模組的使用</summary>

新的 `handlePaymentSuccess` 接受一個物件參數，但該物件的型別並未匯出，其他模組若需要引用此型別會不便。

**建議修法**：考慮匯出一個 `HandlePaymentSuccessParams` 型別。

**判斷依據**：diff 中函式簽章的定義。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/service/BookingAuditTaskerProducerService.ts:405</code> queueBulkRejectedAudit 方法缺少 context 參數的傳遞</summary>

`queueBulkRejectedAudit` 的參數型別中沒有 `context`，但介面 `BookingAuditProducerService` 中定義了 `context?: BookingAuditContext`。這可能導致 context 資訊遺失。

**建議修法**：在參數型別中加入 `context?: BookingAuditContext`，並在呼叫 `queueBulkTask` 時傳遞。

**判斷依據**：diff 中新增的方法，缺少 `context` 參數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 30632 (cache hit 29952) ｜ completion tokens 2708 ｜ PR #10</sub>