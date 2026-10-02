<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 bookings 查詢的權限判斷從「僅 ADMIN/OWNER 角色」改為「透過 PBAC 權限服務」，並在權限服務中新增 orgId 參數以支援組織範圍過濾。主要風險在於 SQL 查詢中 orgId 的型別轉換與條件邏輯可能導致錯誤結果，且測試覆蓋不足，未驗證 orgId 為 null 或 undefined 時的行為。建議優先修正 SQL 條件，並補齊測試。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280` | orgId 為 null 時 SQL 條件可能導致錯誤結果 | 0.95 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309` | orgId 條件在 UNION 第二段可能過濾不正確 | 0.80 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:357` | orgId 條件在 fallback roles 查詢中可能過濾不正確 | 0.80 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:121` | getTeamIdsWithPermission 呼叫未傳遞 orgId | 0.75 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:134` | getEventTypeIdsFromTeamIdsFilter 可能被誤用 | 0.70 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:135` | getUserIdsAndEmailsFromTeamIds 可能未包含組織成員 | 0.70 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:149` | isCurrentUser 判斷變更可能導致權限繞過 | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1` | 測試覆蓋不足，未驗證 orgId 為 null/undefined 的情況 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280</code> orgId 為 null 時 SQL 條件可能導致錯誤結果</summary>

在 `getTeamsWithPBACPermissions` 的 SQL 中，條件 `AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})` 使用 `::bigint` 轉型。若 `orgId` 為 `null`，`${orgId}::bigint` 會是 `NULL::bigint`，`NULL IS NULL` 為 true，因此條件成立，不會過濾。但若 `orgId` 為 `undefined`，Prisma 的 `$queryRaw` 可能將其轉為 `NULL` 或產生錯誤。此外，若 `orgId` 為 0 或負數，條件可能意外匹配。建議明確處理 `orgId` 為 null/undefined 的情況，例如使用 Prisma 的條件式查詢或先判斷再決定是否加入條件。

**判斷依據**：diff 中新增的 SQL 條件，行號約 280。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309</code> orgId 條件在 UNION 第二段可能過濾不正確</summary>

在 `getTeamsWithPBACPermissions` 的 UNION 第二段，條件 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})` 中，`org` 是父組織，`child` 是子團隊。若 `orgId` 指定為父組織 ID，則 `org."id" = ${orgId}` 成立，會包含所有子團隊；若 `orgId` 指定為子團隊 ID，則 `child."id" = ${orgId}` 成立，但 `org."id" = ${orgId}` 不成立，因此只會包含該子團隊。這可能符合預期，但需確認是否應包含父組織本身。建議明確註釋意圖並增加測試。

**判斷依據**：diff 中新增的 SQL 條件，行號約 309。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:357</code> orgId 條件在 fallback roles 查詢中可能過濾不正確</summary>

在 `getTeamsWithFallbackRoles` 的 UNION 第二段，條件 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId} OR child."parentId" = ${orgId})` 中，若 `orgId` 指定為父組織 ID，則 `org."id" = ${orgId}` 成立，會包含所有子團隊；若 `orgId` 指定為子團隊 ID，則 `child."id" = ${orgId}` 或 `child."parentId" = ${orgId}` 成立，但 `org."id" = ${orgId}` 不成立，因此只會包含該子團隊及其子團隊。這可能導致父組織本身未被包含。建議確認預期行為並增加測試。

**判斷依據**：diff 中新增的 SQL 條件，行號約 346。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:121</code> getTeamIdsWithPermission 呼叫未傳遞 orgId</summary>

在 `getBookings` 中呼叫 `permissionCheckService.getTeamIdsWithPermission` 時，傳入了 `orgId: user.orgId ?? undefined`，但 `PermissionCheckService.getTeamIdsWithPermission` 的參數型別為 `orgId?: number`，若 `user.orgId` 為 null，則傳入 undefined，可能導致後續 SQL 查詢中 orgId 為 undefined 而非 null，造成條件判斷錯誤。建議確認 undefined 的處理方式，或改為傳入 null。

**判斷依據**：diff 中新增的呼叫，行號約 118。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:134</code> getEventTypeIdsFromTeamIdsFilter 可能被誤用</summary>

在 `getBookings` 中，原本的 `getEventTypeIdsWhereUserIsAdminOrOwner` 被替換為 `getEventTypeIdsFromTeamIdsFilter(prisma, teamIdsWithBookingPermission)`。但 `getEventTypeIdsFromTeamIdsFilter` 的實作可能只處理直接團隊 ID，未包含子團隊或組織層級，導致權限範圍不完整。建議確認該函數的實作是否符合預期，或改用其他方法。

**判斷依據**：diff 中替換的呼叫，行號約 124。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:135</code> getUserIdsAndEmailsFromTeamIds 可能未包含組織成員</summary>

在 `getBookings` 中，原本的 `getUserIdsAndEmailsWhereUserIsAdminOrOwner` 被替換為 `getUserIdsAndEmailsFromTeamIds(prisma, teamIdsWithBookingPermission)`。但 `getUserIdsAndEmailsFromTeamIds` 只查詢直接屬於這些團隊的用戶，若用戶透過組織成員身分間接屬於團隊，可能未被包含。建議確認是否需包含組織成員。

**判斷依據**：diff 中替換的呼叫，行號約 125。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:149</code> isCurrentUser 判斷變更可能導致權限繞過</summary>

原本的 `isCurrentUser` 判斷為 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示若 `filters.userIds` 包含當前用戶 ID 和其他用戶 ID，則 `isCurrentUser` 為 true，可能導致後續權限檢查放寬，允許存取其他用戶的 bookings。建議確認此變更是否為預期，並增加測試。

**判斷依據**：diff 中變更的判斷，行號約 133。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1</code> 測試覆蓋不足，未驗證 orgId 為 null/undefined 的情況</summary>

新增的測試僅涵蓋 orgId 有值的情況，未測試 orgId 為 null 或 undefined 時的行為。建議增加測試以確保無 orgId 時不會過濾，且不會出錯。

**判斷依據**：測試檔案中未包含 orgId 為 null/undefined 的測試案例。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12284 (cache hit 12160) ｜ completion tokens 2257 ｜ PR #1</sub>