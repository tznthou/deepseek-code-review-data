<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 booking audit 整合至確認/拒絕流程，新增 actor 與 actionSource 參數，並擴充測試。主要風險在於 handleConfirmation 中 acceptedBookings 的 oldStatus 可能不正確、recurring 拒絕流程的 oldStatus 取自更新後狀態、以及 getAppActor 對 apps 為 undefined 的處理。建議優先修正這些正確性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單一預約接受時 acceptedBookings 的 oldStatus 固定為 ACCEPTED | 0.85 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432` | recurring 拒絕時 rejectedBookings 的 oldStatus 取自更新後的狀態 | 0.80 |
| ⚠️ | Major | `packages/app-store/_utils/getAppActor.ts:32` | apps 可能為 undefined 導致 getAppActor 拋出錯誤 | 0.75 |
| 🔸 | Minor | `packages/features/bookings/lib/handleConfirmation.ts:263` | recurring 接受時 acceptedBookings 的 oldStatus 可能不準確 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單一預約接受時 acceptedBookings 的 oldStatus 固定為 ACCEPTED</summary>

在非 recurring 的接受流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時預約尚未更新，其狀態應為 PENDING（或先前的其他狀態）。這會導致 audit log 中記錄的狀態變更不正確（old 與 new 皆為 ACCEPTED）。

建議改為使用更新前的 `booking.status`，例如：
```ts
acceptedBookings = [{ oldStatus: booking.status, uid: booking.uid }];
```

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation 函式內，非 recurring 分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432</code> recurring 拒絕時 rejectedBookings 的 oldStatus 取自更新後的狀態</summary>

在 recurring 拒絕流程中，先執行 `prisma.booking.updateMany` 將狀態改為 REJECTED，然後再查詢這些預約並將 `oldStatus` 設為查詢到的 `status`（此時已是 REJECTED）。這會使 audit log 中的 `oldStatus` 錯誤地顯示為 REJECTED，而非原本的 PENDING。

建議在更新前先取得原始狀態，或直接使用已知的 PENDING（因為查詢條件已限定 `status: BookingStatus.PENDING`）。

**判斷依據**：diff 中新增的程式碼片段，位於 confirmHandler 的拒絕分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/getAppActor.ts:32</code> apps 可能為 undefined 導致 getAppActor 拋出錯誤</summary>

`getAppActor` 的參數 `apps` 型別為 `z.infer<typeof eventTypeAppMetadataOptionalSchema>`，但呼叫端可能傳入 `undefined`（例如 `eventType?.metadata?.apps` 可能不存在）。在函式內直接使用 `apps?.[appSlug as keyof typeof apps]` 時，若 `apps` 為 undefined，可選鏈會短路，但後續的 `appData?.credentialId` 仍會嘗試存取 `appData`，而 `appData` 的型別可能包含 undefined，但實際上若 `apps` 為 undefined，`appData` 也會是 undefined，這不會拋錯。然而，若 `apps` 為 null（而非 undefined），則 `apps?.[...]` 仍會拋出 TypeError。

建議在函式開頭明確處理 `apps` 為 null/undefined 的情況，或使用更安全的存取方式。

**判斷依據**：diff 中新增的 getAppActor.ts 檔案，第 31 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:263</code> recurring 接受時 acceptedBookings 的 oldStatus 可能不準確</summary>

在 recurring 接受流程中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 映射而來，其 `oldStatus` 取自 `booking.status`。但 `unconfirmedRecurringBookings` 的查詢條件是 `status: BookingStatus.PENDING`，因此 `oldStatus` 應為 PENDING。然而，若查詢條件未來變更，或存在其他狀態的預約，此處可能記錄錯誤。目前影響不大，但建議明確使用 `BookingStatus.PENDING` 或保留原始狀態。

**判斷依據**：diff 中新增的程式碼片段，位於 handleConfirmation 的 recurring 分支。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 30008 (cache hit 29952) ｜ completion tokens 1364 ｜ PR #10</sub>