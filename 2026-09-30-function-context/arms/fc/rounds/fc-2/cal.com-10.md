<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 整合了 booking audit 功能，新增了多個呼叫點的 actor 與 actionSource 參數，並加入了 magic link 來源。主要風險在於 `handleConfirmation` 中單筆 booking 的 `acceptedBookings` 使用了錯誤的舊狀態（硬編碼為 ACCEPTED），可能導致 audit log 不正確；此外 `confirmHandler` 中 reject 流程的 `oldStatus` 取自更新後的狀態，同樣有誤。另有 `handlePaymentSuccess` 中 `eventType` 可能為 null 的潛在錯誤，以及 `getAppActor` 的型別安全疑慮。建議修正上述問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 acceptedBookings 使用錯誤的舊狀態 | 0.90 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468` | reject 流程中 rejectedBookings 的 oldStatus 取自更新後的狀態 | 0.85 |
| ⚠️ | Major | `packages/app-store/_utils/payments/handlePaymentSuccess.ts:48` | eventType 可能為 null 時解析 apps 導致錯誤 | 0.80 |
| 🔸 | Minor | `packages/app-store/_utils/getAppActor.ts:32` | getAppActor 中 apps 的型別可能不正確 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 acceptedBookings 使用錯誤的舊狀態</summary>

在非 recurring 分支中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`，但此時 booking 尚未更新，其狀態應為 `booking.status`（可能是 PENDING）。這會導致 audit log 中的 `status.old` 永遠是 ACCEPTED，而非實際的舊狀態。

**失敗情境**：當一個 PENDING booking 被確認時，audit log 會記錄 `old: ACCEPTED, new: ACCEPTED`，無法反映狀態變更。

**建議**：改為 `oldStatus: booking.status`。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation 的非 recurring 分支，直接將 oldStatus 設為 BookingStatus.ACCEPTED，而未使用 booking.status。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468</code> reject 流程中 rejectedBookings 的 oldStatus 取自更新後的狀態</summary>

在非 recurring 的 reject 分支中，先執行了 `prisma.booking.update` 將狀態改為 REJECTED，然後才設定 `rejectedBookings = [{ uid: booking.uid, oldStatus: booking.status }]`。此時 `booking.status` 仍是更新前的值（因為 `booking` 物件是先前查詢的結果），但若後續有重新查詢，則可能取得更新後的值。目前程式碼中 `booking.status` 是更新前的值，但依賴於物件未變更，較脆弱。

**失敗情境**：若未來在更新後重新取得 booking，oldStatus 會變成 REJECTED，導致 audit log 錯誤。

**建議**：在更新前先保存舊狀態，例如 `const oldStatus = booking.status;`，然後使用該變數。

**判斷依據**：diff 中新增的程式碼片段，位於 confirmHandler 的 reject 非 recurring 分支，在 prisma.booking.update 之後設定 rejectedBookings，使用 booking.status 作為 oldStatus。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/payments/handlePaymentSuccess.ts:48</code> eventType 可能為 null 時解析 apps 導致錯誤</summary>

`const apps = eventTypeAppMetadataOptionalSchema.parse(eventType?.metadata?.apps);` 中，`eventType` 可能為 null（從 `getBooking` 回傳的型別推斷），若為 null，則 `eventType?.metadata?.apps` 為 undefined，`eventTypeAppMetadataOptionalSchema.parse(undefined)` 可能拋出錯誤。

**失敗情境**：當 booking 沒有 eventType 時，此行程式碼會拋出 ZodError，導致整個 payment success 處理失敗。

**建議**：先檢查 `eventType` 是否存在，或使用 `eventType?.metadata?.apps ?? {}` 提供預設值。

**判斷依據**：diff 中新增的程式碼，位於 handlePaymentSuccess 函式開頭，直接對可能為 null 的 eventType 進行 parse。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/app-store/_utils/getAppActor.ts:32</code> getAppActor 中 apps 的型別可能不正確</summary>

`const appData = apps?.[appSlug as keyof typeof apps];` 使用 `keyof typeof apps` 可能無法正確索引，因為 `apps` 的型別是 `z.infer<typeof eventTypeAppMetadataOptionalSchema>`，其鍵值可能不是 string。若 `appSlug` 不存在於 apps 中，`appData` 會是 undefined，但型別上可能被認為是存在的。

**失敗情境**：當 appSlug 不在 apps 中時，`appData?.credentialId` 會是 undefined，但 TypeScript 可能不會報錯，導致 fallback 邏輯未被觸發。

**建議**：使用更安全的型別，例如 `Record<string, { credentialId?: number }>` 或先檢查 `appSlug in apps`。

**判斷依據**：diff 中新增的 getAppActor 函式，使用 keyof typeof apps 進行索引，可能導致型別不安全。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 59221 (cache hit 59136) ｜ completion tokens 1446 ｜ PR #10</sub>