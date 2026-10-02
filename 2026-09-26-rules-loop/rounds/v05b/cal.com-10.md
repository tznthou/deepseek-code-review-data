<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要整合 booking audit 功能，在多個入口（API v2、magic link、webhook、tRPC）傳遞 actor 與 actionSource，並新增 bulk rejected audit 支援。主要風險在於 `handleConfirmation.ts` 中單筆 booking 的 `oldStatus` 被硬編碼為 `ACCEPTED`，可能導致 audit log 記錄錯誤；此外 `getAppActor` 在缺少 credentialId 時僅以 slug 建立 actor，可能造成 actor 識別混淆。整體變更範圍大，建議修正上述問題後再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED，導致 audit log 不正確 | 0.95 |
| ⚠️ | Major | `packages/app-store/_utils/getAppActor.ts:43` | 缺少 credentialId 時僅以 appSlug 建立 actor，可能導致 actor 識別混淆 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring booking 的 oldStatus 可能不正確 | 0.75 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468` | rejectedBookings 的 oldStatus 可能不正確 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:85` | fireBookingAcceptedEvent 的錯誤處理可能隱藏問題 | 0.60 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:55` | fireBookingAcceptedEvent 的 tracingLogger 型別可能不符 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED，導致 audit log 不正確</summary>

在 `handleConfirmation` 中，當處理非 recurring 的 booking 時，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 `PENDING` 或其他非 `ACCEPTED` 狀態，這會導致 audit log 中記錄的 `oldStatus` 錯誤。

**失敗情境**：一個 `PENDING` 狀態的 booking 被確認後，audit log 會顯示 `oldStatus: ACCEPTED`，而非 `PENDING`。

**建議**：應從資料庫中取得 booking 的實際狀態，例如在更新前先查詢 `booking.status`，或使用 `updatedBooking.status`（如果 Prisma 回傳更新前的狀態）。

**判斷依據**：diff 中新增的程式碼片段，位於 `handleConfirmation.ts` 的 `else` 分支，將 `oldStatus` 固定為 `BookingStatus.ACCEPTED`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/getAppActor.ts:43</code> 缺少 credentialId 時僅以 appSlug 建立 actor，可能導致 actor 識別混淆</summary>

`getAppActor` 在 `appData?.credentialId` 不存在時，使用 `makeAppActorUsingSlug` 建立 actor。這可能導致多個相同 app 的不同 credential 被視為同一 actor，影響 audit log 的準確性。

**失敗情境**：同一個 app（例如 stripe）有多個 credential，但其中一個沒有 credentialId，則所有缺少 credentialId 的事件都會被歸因到同一個 actor。

**建議**：考慮使用其他唯一識別碼（例如 app 的 id 或 instance id）來建立 actor，或至少記錄更詳細的資訊。

**判斷依據**：diff 中新增的 `getAppActor.ts` 檔案，在 fallback 路徑使用 `makeAppActorUsingSlug`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring booking 的 oldStatus 可能不正確</summary>

在處理 recurring booking 時，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 取得，其 `status` 欄位是從資料庫查詢的。但後續的 `updateMany` 會將所有符合條件的 booking 更新為 `ACCEPTED`，而 `acceptedBookings` 中的 `oldStatus` 是更新前的狀態，這部分正確。然而，如果 `unconfirmedRecurringBookings` 中包含非 `PENDING` 狀態的 booking（例如 `REJECTED`），則 audit log 會記錄錯誤的 `oldStatus`。

**失敗情境**：一個 recurring booking 中，某個子 booking 已經被拒絕，但整體確認時仍被包含在 `unconfirmedRecurringBookings` 中，導致 audit log 記錄 `oldStatus: REJECTED` 而非 `PENDING`。

**建議**：確認 `unconfirmedRecurringBookings` 的查詢條件是否正確（目前為 `status: BookingStatus.PENDING`），並考慮在 audit log 中記錄實際的狀態變化。

**判斷依據**：diff 中新增的程式碼片段，位於 `handleConfirmation.ts` 的 recurring 分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468</code> rejectedBookings 的 oldStatus 可能不正確</summary>

在 `confirmHandler` 的 reject 分支中，單筆 booking 的 `oldStatus` 使用 `booking.status`，但此時 `booking` 是從資料庫查詢的原始物件，其狀態可能尚未更新。如果 booking 原本是 `PENDING`，則 `oldStatus` 正確；但如果 booking 原本是其他狀態（例如 `ACCEPTED`），則 audit log 會記錄錯誤。

**失敗情境**：一個已接受的 booking 被拒絕（可能透過某些流程），audit log 會記錄 `oldStatus: ACCEPTED`，但實際狀態變化是 `ACCEPTED` → `REJECTED`。

**建議**：確認此處的 `booking.status` 是否為更新前的狀態，並考慮使用更新後的狀態來驗證。

**判斷依據**：diff 中新增的程式碼片段，位於 `confirm.handler.ts` 的 reject 分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:85</code> fireBookingAcceptedEvent 的錯誤處理可能隱藏問題</summary>

`fireBookingAcceptedEvent` 內部使用 try-catch 並僅記錄錯誤，這可能導致 audit log 遺失而不被察覺。雖然 audit 不應阻礙主要流程，但建議至少增加監控或告警。

**失敗情境**：audit 服務暫時不可用，所有 audit log 遺失，但系統沒有明顯錯誤。

**建議**：考慮在 catch 中增加 metric 或 sentry 報告。

**判斷依據**：diff 中新增的 `fireBookingAcceptedEvent` 函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:55</code> fireBookingAcceptedEvent 的 tracingLogger 型別可能不符</summary>

`fireBookingAcceptedEvent` 的參數 `tracingLogger` 型別為 `ISimpleLogger`，但呼叫時傳入的 `tracingLogger` 是從 `handleConfirmation` 的參數中取得的，其型別可能不是 `ISimpleLogger`。需要確認型別相容性。

**失敗情境**：如果型別不相容，TypeScript 編譯會失敗。

**建議**：檢查 `handleConfirmation` 中 `tracingLogger` 的實際型別，並確保與 `ISimpleLogger` 相容。

**判斷依據**：diff 中新增的函式簽名。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31416 (cache hit 31360) ｜ completion tokens 2013 ｜ PR #10</sub>