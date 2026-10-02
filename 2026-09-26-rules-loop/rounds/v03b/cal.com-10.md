<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要為 booking confirmation/rejection 流程加入 booking audit 整合，包含新增 actor 與 actionSource 參數、新增 MAGIC_LINK 來源、以及相關測試。主要風險在於 handleConfirmation 中 acceptedBookings 的 oldStatus 可能不正確、recurring booking 的 rejectedBookings 記錄的 oldStatus 有誤、以及 getAppActor 的型別安全性不足。建議先修正這些正確性問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | acceptedBookings 的 oldStatus 硬編碼為 ACCEPTED，可能導致 audit log 記錄錯誤的狀態變更 | 0.95 |
| 🛑 | Blocker | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432` | recurring booking 的 rejectedBookings 記錄的 oldStatus 為更新後的狀態，而非更新前的狀態 | 0.90 |
| ⚠️ | Major | `packages/app-store/_utils/getAppActor.ts:32` | getAppActor 使用型別不安全的索引存取，可能導致 runtime 錯誤 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring booking 的 acceptedBookings 使用 unconfirmedRecurringBookings 的 status，但該查詢可能未包含所有需 | 0.75 |
| 🔸 | Minor | `packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19` | RejectedAuditActionService 的 fieldsSchemaV1 中 rejectionReason 改為 z.string().nullable()，可能影 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> acceptedBookings 的 oldStatus 硬編碼為 ACCEPTED，可能導致 audit log 記錄錯誤的狀態變更</summary>

在非 recurring 的單一 booking 確認流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 PENDING（或甚至是其他狀態），硬編碼為 ACCEPTED 會讓 audit log 記錄錯誤的 previousStatus。

**失敗情境**：當一個 PENDING booking 被確認時，audit log 會顯示 previousStatus=ACCEPTED, newStatus=ACCEPTED，而不是正確的 PENDING→ACCEPTED。

**建議**：從資料庫取得 booking 的實際狀態，例如在更新前先查詢 `booking.status`，或使用 `updatedBooking.status`（如果 update 有回傳舊值）。

**判斷依據**：diff 中新增的程式碼片段，在非 recurring 分支中直接將 oldStatus 設為 BookingStatus.ACCEPTED，未考慮 booking 的實際狀態。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432</code> recurring booking 的 rejectedBookings 記錄的 oldStatus 為更新後的狀態，而非更新前的狀態</summary>

在 recurring booking 的拒絕流程中，先執行 `prisma.booking.updateMany` 將所有 PENDING bookings 更新為 REJECTED，然後再查詢這些 bookings 的狀態並填入 `rejectedBookings`。此時查詢到的 `status` 已經是 REJECTED，因此 `oldStatus` 會被記錄為 REJECTED，而不是更新前的 PENDING。

**失敗情境**：audit log 會顯示 previousStatus=REJECTED, newStatus=REJECTED，而不是正確的 PENDING→REJECTED。

**建議**：在更新前先查詢並保存每個 booking 的原始狀態，例如使用 `unconfirmedRecurringBookings` 的 `status` 欄位，而不是更新後再查詢。

**判斷依據**：diff 中顯示在 updateMany 之後才查詢 status，並將該 status 作為 oldStatus。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/getAppActor.ts:32</code> getAppActor 使用型別不安全的索引存取，可能導致 runtime 錯誤</summary>

`apps?.[appSlug as keyof typeof apps]` 使用了型別斷言來索引 apps 物件。如果 `appSlug` 不是 apps 物件的有效 key，這個表達式會回傳 `undefined`，但 TypeScript 不會報錯。雖然後續有檢查 `appData?.credentialId`，但若 `appData` 為 `undefined`，則會進入 fallback 分支，這可能不是預期行為。

**失敗情境**：如果傳入的 `appSlug` 不存在於 apps 物件中，會錯誤地使用 fallback 建立 actor，而不是拋出錯誤或明確處理。

**建議**：使用更安全的存取方式，例如 `apps?.[appSlug]` 並搭配型別保護，或使用 `Object.prototype.hasOwnProperty` 檢查。

**判斷依據**：diff 中新增的 getAppActor 函式，使用了型別斷言來索引 apps 物件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring booking 的 acceptedBookings 使用 unconfirmedRecurringBookings 的 status，但該查詢可能未包含所有需要的欄位</summary>

在 recurring booking 的確認流程中，`unconfirmedRecurringBookings` 是透過 `prisma.booking.findMany` 查詢的，但 select 欄位只包含 `id` 和 `uid`（從 diff 中可見）。然而，後續使用 `booking.status` 來設定 `oldStatus`，這可能導致 `status` 為 `undefined`。

**失敗情境**：如果 `unconfirmedRecurringBookings` 的 select 沒有包含 `status`，則 `oldStatus` 會是 `undefined`，導致 audit log 記錄錯誤。

**建議**：確認 `unconfirmedRecurringBookings` 的 select 包含 `status` 欄位，或直接使用已知的 PENDING 狀態（因為查詢條件是 `status: BookingStatus.PENDING`）。

**判斷依據**：diff 中顯示 acceptedBookings 使用 booking.status，但未顯示 unconfirmedRecurringBookings 的 select 是否包含 status。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19</code> RejectedAuditActionService 的 fieldsSchemaV1 中 rejectionReason 改為 z.string().nullable()，可能影響既有資料的相容性</summary>

原本的 `rejectionReason` 使用 `StringChangeSchema`（可能包含 old/new 結構），現在改為 `z.string().nullable()`。這會影響已儲存的 audit log 資料的解析，可能導致舊資料無法正確讀取。

**失敗情境**：如果資料庫中已有舊格式的 rejectionReason（例如 `{ old: ..., new: ... }`），新的 schema 會解析失敗，導致 audit log 無法顯示。

**建議**：確認是否有 migration 或相容性處理，或保留舊 schema 並提供轉換邏輯。

**判斷依據**：diff 中顯示 rejectionReason 的 schema 從 StringChangeSchema 改為 z.string().nullable()。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31457 (cache hit 31360) ｜ completion tokens 1888 ｜ PR #10</sub>