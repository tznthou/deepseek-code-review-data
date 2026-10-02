<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 將 booking 查詢的權限判斷從 ADMIN/OWNER 角色改為 PBAC 權限，並新增 orgId 參數以支援組織範圍。主要風險在於測試檔案中大量使用 `as any` 與不完整的 mock，可能導致測試不穩定或誤判；此外，`get.handler.ts` 中 `getBookings` 函式未處理 `getTeamIdsWithPermission` 回傳空陣列時的行為，可能造成權限判斷錯誤。建議先修正測試的型別安全與 mock 完整性，並確認空陣列情境下的權限邏輯。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1` | [R08] 測試檔案使用 `as any` 規避型別檢查，可能隱藏錯誤 | 0.90 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1` | [R08] 測試中的 mock 不完整，可能導致測試不穩定 | 0.85 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:111` | 未處理 `getTeamIdsWithPermission` 回傳空陣列時的行為 | 0.80 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:117` | `getTeamIdsWithPermission` 可能回傳空陣列，但後續邏輯未處理 | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:121` | `getTeamIdsWithPermission` 的 `orgId` 參數可能導致權限範圍錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1</code> [R08] 測試檔案使用 `as any` 規避型別檢查，可能隱藏錯誤</summary>

測試檔案中多處使用 `as any`（例如 `mockBookings`、`mockUser as any`、`mockPrisma as unknown as PrismaClient`），這會繞過 TypeScript 的型別檢查，使得測試無法捕捉到型別錯誤。建議使用正確的型別或建立完整的 mock 物件，以確保測試的可靠性。

**判斷依據**：diff 中新增的測試檔案大量使用 `as any`，例如 `mockBookings` 的宣告。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1</code> [R08] 測試中的 mock 不完整，可能導致測試不穩定</summary>

測試中對 `kysely` 的 mock 僅實作了部分方法（如 `selectFrom`、`executeQuery`），但實際程式碼可能呼叫其他方法（如 `select`、`where`、`innerJoin` 等）。若 mock 未涵蓋所有使用的方法，測試可能因 `undefined is not a function` 而失敗。建議使用完整的 mock 或使用 `vi.mock` 自動模擬整個模組。

**判斷依據**：diff 中 `createMockKysely` 僅回傳包含 `selectFrom` 和 `executeQuery` 的物件，但 `getBookings` 中使用了 `kysely.selectFrom(...).select(...).where(...)` 等鏈式呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:111</code> 未處理 `getTeamIdsWithPermission` 回傳空陣列時的行為</summary>

當 `getTeamIdsWithPermission` 回傳空陣列時，`teamIdsWithBookingPermission` 為空，後續的 `getEventTypeIdsFromTeamIdsFilter` 和 `getUserIdsAndEmailsFromTeamIds` 會以空陣列為參數。這可能導致查詢條件不正確，例如 `where: { teamId: { in: [] } }` 可能回傳所有資料或拋出錯誤。建議明確處理空陣列的情況，例如直接回傳空結果或拋出權限錯誤。

**判斷依據**：diff 中新增了 `teamIdsWithBookingPermission` 的取得，但未檢查其是否為空陣列。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:117</code> `getTeamIdsWithPermission` 可能回傳空陣列，但後續邏輯未處理</summary>

`getTeamIdsWithPermission` 在權限驗證失敗時會回傳空陣列（見 `permission-check.service.ts` 的實作）。若使用者沒有任何權限，`teamIdsWithBookingPermission` 為空，但後續的 `getEventTypeIdsFromTeamIdsFilter` 和 `getUserIdsAndEmailsFromTeamIds` 仍會被呼叫，可能導致不必要的查詢或錯誤。建議在取得權限後立即檢查，若為空則直接回傳空結果。

**判斷依據**：diff 中新增了權限檢查，但未處理空陣列的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:121</code> `getTeamIdsWithPermission` 的 `orgId` 參數可能導致權限範圍錯誤</summary>

`getTeamIdsWithPermission` 新增了 `orgId` 參數，但呼叫時傳入 `user.orgId ?? undefined`。若 `user.orgId` 為 `null`，則傳入 `undefined`，這可能導致查詢條件中 `orgId` 為 `NULL` 時的行為與預期不符。建議確認 `orgId` 為 `null` 時是否應視為無限制，並在 repository 層明確處理。

**判斷依據**：diff 中呼叫 `getTeamIdsWithPermission` 時傳入 `orgId: user.orgId ?? undefined`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13760 (cache hit 13696) ｜ completion tokens 1407 ｜ PR #1</sub>