<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要整合 booking audit 功能，在多個入口（API v2、magic link、webhook、tRPC）傳遞 actor 與 actionSource，並新增 bulk rejected audit 支援。整體方向合理，但存在幾個需要修正的問題：最嚴重的是 `handleConfirmation` 中單筆 booking 的 `oldStatus` 被硬編碼為 `ACCEPTED`，可能導致 audit log 記錄錯誤；其次是 `confirmHandler` 中 bulk reject 的 `oldStatus` 取自更新後的狀態，同樣會記錄錯誤。此外，`getAppActor` 的 fallback 邏輯可能產生不正確的 actor，且部分測試的 mock 設定可能不完整。建議修正這些正確性問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED，導致 audit log 記錄錯誤 | 0.95 |
| 🛑 | Blocker | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432` | bulk reject 的 oldStatus 取自更新後的狀態，導致 audit log 記錄錯誤 | 0.90 |
| ⚠️ | Major | `packages/app-store/_utils/getAppActor.ts:33` | getAppActor 的 fallback 邏輯可能產生不正確的 actor | 0.80 |
| 🔸 | Minor | `apps/web/app/api/link/__tests__/route.test.ts:81` | 測試中 mock 的 makeUserActor 可能未正確設定 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED，導致 audit log 記錄錯誤</summary>

在 `handleConfirmation` 中，當處理單筆 booking（非 recurring）時，`acceptedBookings` 陣列的 `oldStatus` 被直接設定為 `BookingStatus.ACCEPTED`。這會導致 audit log 中的 `status.old` 永遠是 `ACCEPTED`，即使 booking 原本是 `PENDING` 或其他狀態。

**失敗情境**：一個 `PENDING` 狀態的 booking 被確認後，audit log 會顯示狀態從 `ACCEPTED` 變為 `ACCEPTED`，而不是從 `PENDING` 變為 `ACCEPTED`。

**建議修法**：從 `booking` 物件取得實際的舊狀態，例如：
```ts
acceptedBookings = [
  {
    oldStatus: booking.status,
    uid: booking.uid,
  },
];
```

**判斷依據**：diff 中新增的程式碼片段，在 `handleConfirmation` 的單筆 booking 分支中，`oldStatus` 被硬編碼為 `BookingStatus.ACCEPTED`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432</code> bulk reject 的 oldStatus 取自更新後的狀態，導致 audit log 記錄錯誤</summary>

在 `confirmHandler` 的 reject 分支中，當處理 recurring booking 時，先執行 `prisma.booking.updateMany` 將所有符合條件的 booking 狀態改為 `REJECTED`，然後再查詢這些 booking 的 `status` 並將其作為 `oldStatus`。這會導致 `oldStatus` 永遠是 `REJECTED`，而不是更新前的 `PENDING`。

**失敗情境**：一個 `PENDING` 的 recurring booking 被拒絕後，audit log 會顯示狀態從 `REJECTED` 變為 `REJECTED`，而不是從 `PENDING` 變為 `REJECTED`。

**建議修法**：在更新前先查詢並保存舊狀態，例如使用 `unconfirmedRecurringBookings` 中的 `status` 作為 `oldStatus`。

**判斷依據**：diff 中新增的程式碼片段，在 `confirmHandler` 的 reject 分支中，`oldStatus` 取自更新後的 `status`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/getAppActor.ts:33</code> getAppActor 的 fallback 邏輯可能產生不正確的 actor</summary>

在 `getAppActor` 中，當 `appData?.credentialId` 不存在時，會使用 `makeAppActorUsingSlug` 建立 actor。然而，`makeAppActorUsingSlug` 可能無法正確識別 app 實例，特別是在同一 app 有多個 credential 的情況下。這可能導致 audit log 中的 actor 不準確。

**失敗情境**：如果一個 event type 安裝了多個相同 app（例如多個 Stripe 帳號），且其中一個沒有 credentialId，則 fallback 會使用 slug 建立 actor，無法區分是哪一個 credential 觸發了操作。

**建議修法**：考慮是否應該在缺少 credentialId 時直接拋出錯誤，或者使用其他方式來識別 app 實例。

**判斷依據**：diff 中新增的 `getAppActor` 函式，其 fallback 邏輯可能導致 actor 不準確。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/app/api/link/__tests__/route.test.ts:81</code> 測試中 mock 的 makeUserActor 可能未正確設定</summary>

在 `apps/web/app/api/link/__tests__/route.test.ts` 中，新增了 `vi.mock("@calcom/features/booking-audit/lib/makeActor", ...)`，但未檢查該 mock 是否在測試中正確使用。如果 `makeUserActor` 在測試中被呼叫，但 mock 未正確設定，可能導致測試失敗或產生非預期行為。

**建議修法**：確認 mock 的設定與實際使用一致，並在測試中驗證 `makeUserActor` 是否被正確呼叫。

**判斷依據**：diff 中新增的 mock 設定，但未確認其使用方式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 30632 (cache hit 30592) ｜ completion tokens 1729 ｜ PR #10</sub>