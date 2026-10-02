<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要整合 booking audit 功能：在確認/拒絕訂位時記錄 actor 與 actionSource，並新增 MAGIC_LINK 來源與 bulk reject 事件。整體方向合理，但存在幾個需要修正的問題：`handleConfirmation` 中單筆訂位接受時 `oldStatus` 被硬編碼為 `ACCEPTED`，可能導致 audit log 不正確；`confirmHandler` 中 bulk reject 的 `oldStatus` 取自更新後的狀態，同樣會造成 audit 資料錯誤；`getAppActor` 使用 `apps?.[appSlug]` 可能因 key 型別不符而無法取得 credentialId；此外，部分測試的 mock 設定可能不完整，且新增的 `getAppActor` 檔案違反了 R01 命名規範。建議優先修正 audit 資料的正確性問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/bookings/lib/handleConfirmation.ts:411` | 單筆訂位接受時 oldStatus 被硬編碼為 ACCEPTED，導致 audit log 不正確 | 0.95 |
| 🛑 | Blocker | `packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432` | Bulk reject 時 oldStatus 取自更新後的狀態，導致 audit log 不正確 | 0.90 |
| ⚠️ | Major | `packages/app-store/_utils/getAppActor.ts:32` | getAppActor 使用 apps?.[appSlug] 可能因 key 型別不符而無法取得 credentialId | 0.80 |
| 🔸 | Minor | `packages/app-store/_utils/getAppActor.ts:22` | [R01] 檔案名稱不符合 Repository/Service 命名規範 | 0.70 |
| 🔸 | Minor | `apps/web/app/api/link/__tests__/route.test.ts:81` | 測試中 mock 的 makeUserActor 可能未正確模擬實際行為 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/bookings/lib/handleConfirmation.ts:411</code> 單筆訂位接受時 oldStatus 被硬編碼為 ACCEPTED，導致 audit log 不正確</summary>

在 `handleConfirmation` 中，當處理非 recurring 的單筆訂位時，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時訂位尚未更新，其狀態應為 `PENDING`（或先前的狀態），而非 `ACCEPTED`。這會導致 audit log 中記錄的狀態變更為 `ACCEPTED -> ACCEPTED`，失去稽核意義。

**失敗情境**：任何單筆訂位確認後，查詢 audit log 會看到 `previousStatus` 與 `newStatus` 皆為 `ACCEPTED`，無法反映實際的狀態轉換。

**建議**：在更新前先取得訂位的原始狀態，例如從 `booking` 物件中讀取 `booking.status`，並使用該值作為 `oldStatus`。

**判斷依據**：diff 中新增的程式碼片段，位於 `handleConfirmation` 函式內，在 `updatedBookings.push(updatedBooking)` 之後。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432</code> Bulk reject 時 oldStatus 取自更新後的狀態，導致 audit log 不正確</summary>

在 `confirmHandler` 的 reject 分支中，對於 recurring bookings，程式先執行 `prisma.booking.updateMany` 將狀態改為 `REJECTED`，然後再查詢這些 bookings 並將查詢結果的 `status` 作為 `oldStatus` 放入 `rejectedBookings`。這會導致 `oldStatus` 永遠是 `REJECTED`，而非實際的舊狀態（應為 `PENDING`）。

**失敗情境**：任何 bulk reject 操作後，audit log 會顯示 `REJECTED -> REJECTED`，無法反映狀態變更。

**建議**：在更新前先查詢並保存原始狀態，例如使用 `unconfirmedRecurringBookings` 中的 `status` 作為 `oldStatus`，而不是更新後再查詢。

**判斷依據**：diff 中新增的程式碼片段，位於 `confirmHandler` 的 reject 分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/app-store/_utils/getAppActor.ts:32</code> getAppActor 使用 apps?.[appSlug] 可能因 key 型別不符而無法取得 credentialId</summary>

`apps` 的型別是 `z.infer<typeof eventTypeAppMetadataOptionalSchema>`，其 key 是 app slug 的字串，但 `appSlug` 參數是 `string`。使用 `apps?.[appSlug as keyof typeof apps]` 可能因為型別不符而無法正確索引，導致即使有 credentialId 也無法取得，而 fallback 到 `makeAppActorUsingSlug`。

**失敗情境**：當 event type 的 app metadata 中包含該 app 的 credentialId 時，由於索引型別問題，可能無法取得 credentialId，導致 actor 使用 slug 而非 credentialId，影響 audit log 的精確性。

**建議**：確認 `eventTypeAppMetadataOptionalSchema` 的型別定義，並使用型別安全的索引方式，例如先將 `apps` 轉為 `Record<string, ...>` 或使用 `Object.prototype.hasOwnProperty` 檢查。

**判斷依據**：diff 中新增的 `getAppActor` 函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/app-store/_utils/getAppActor.ts:22</code> [R01] 檔案名稱不符合 Repository/Service 命名規範</summary>

新增的 `getAppActor.ts` 檔案位於 `packages/app-store/_utils/` 下，其內容是一個 utility function，而非 repository 或 service class。根據規範 R01，repository 和 service 檔案應遵循特定命名模式，但此檔案可能不屬於這兩類，因此不一定違反。然而，如果此檔案被視為 service，則其名稱應為 `AppActorService.ts` 並 export 對應的 class。目前它 export 一個 function，可能不符合規範。

**建議**：確認此檔案的角色，若為 service，請改為 class 並遵循命名；若為 utility，則可能不受此規範限制，但需確保團隊共識。

**判斷依據**：diff 中新增的檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/app/api/link/__tests__/route.test.ts:81</code> 測試中 mock 的 makeUserActor 可能未正確模擬實際行為</summary>

在測試中，`makeUserActor` 被 mock 為回傳 `{ type: "user", id: "test-uuid" }`，但實際的 `makeUserActor` 可能回傳更複雜的物件（例如包含 displayName 等）。這可能導致測試無法捕捉到實際使用上的問題。

**建議**：確認 mock 的回傳值與實際實作一致，或使用更精確的 mock 以反映真實行為。

**判斷依據**：diff 中新增的 mock。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31416 (cache hit 29952) ｜ completion tokens 1869 ｜ PR #10</sub>