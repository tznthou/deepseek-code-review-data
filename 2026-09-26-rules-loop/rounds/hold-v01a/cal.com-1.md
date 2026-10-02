<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 bookings 查詢的權限判斷從「僅 ADMIN/OWNER 角色」改為「透過 PBAC 權限服務」，並在權限查詢中新增 orgId 參數以支援組織範圍過濾。主要風險在於 SQL 查詢中 orgId 的型別轉換與邏輯可能導致錯誤結果，且測試覆蓋不足。最應先確認 orgId 為 0 或 null 時的行為，以及 child team 的過濾條件是否正確。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280` | orgId 為 0 時可能被錯誤視為未提供 | 0.80 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309` | child team 過濾條件可能排除應包含的團隊 | 0.75 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:357` | fallback roles 查詢的 child team 過濾條件可能不一致 | 0.75 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:117` | 權限服務回傳空陣列時可能導致查詢範圍錯誤 | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:149` | isCurrentUser 判斷邏輯變更可能影響行為 | 0.60 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:126` | 測試檔案中 mock 的 Kysely 可能無法完全模擬實際行為 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280</code> orgId 為 0 時可能被錯誤視為未提供</summary>

在 SQL 條件 `(${orgId}::bigint IS NULL OR ...)` 中，若 orgId 為 0，則 `0::bigint IS NULL` 為 false，因此會進入後面的 OR 條件。但若 orgId 為 0 且資料庫中沒有 id 為 0 的 team，則結果會是空集合，而非預期的「不限制 orgId」。這可能導致呼叫端傳入 0 時意外地得不到任何結果。建議在 TypeScript 層先將 orgId 轉為 null 或 undefined，或明確處理 0 的情況。

**判斷依據**：diff 中新增的 orgId 條件，若 orgId 為 0 時，`${orgId}::bigint IS NULL` 為 false，且後續 OR 條件可能不成立，導致空結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309</code> child team 過濾條件可能排除應包含的團隊</summary>

在 UNION 的第二個查詢中，條件為 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`。此條件只允許 org 本身或 child 等於 orgId，但若 orgId 是父組織，則 child 的 parentId 等於 orgId 的團隊不會被包含。這可能導致當 orgId 指定為父組織時，其下所有子團隊都被排除，與預期行為不符。建議改為 `child."parentId" = ${orgId}` 或加入 parentId 條件。

**判斷依據**：diff 中新增的條件，與第一個查詢的 `t."parentId" = ${orgId}` 不一致，可能遺漏子團隊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:357</code> fallback roles 查詢的 child team 過濾條件可能不一致</summary>

在 fallback roles 的 UNION 第二個查詢中，條件為 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId} OR child."parentId" = ${orgId})`。此條件包含了 `child."parentId" = ${orgId}`，但第一個查詢（PBAC）的對應條件卻沒有包含 parentId。這可能導致兩種查詢在 orgId 過濾時行為不一致，造成權限判斷錯誤。建議統一兩處的過濾邏輯。

**判斷依據**：diff 中 fallback roles 查詢新增的條件，與 PBAC 查詢的條件不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:117</code> 權限服務回傳空陣列時可能導致查詢範圍錯誤</summary>

`getTeamIdsWithPermission` 在發生錯誤時會回傳空陣列（見 service 中的 catch），而此處直接使用回傳的 `teamIdsWithBookingPermission` 作為後續查詢的輸入。若權限服務因錯誤回傳空陣列，則 `getEventTypeIdsFromTeamIdsFilter` 和 `getUserIdsAndEmailsFromTeamIds` 會收到空陣列，導致後續查詢條件為空，可能回傳空結果或觸發其他錯誤。建議在 service 層區分「無權限」與「查詢失敗」，或在 handler 中處理空陣列的情況。

**判斷依據**：diff 中新增的呼叫，且 service 的 catch 區塊會回傳空陣列。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:149</code> isCurrentUser 判斷邏輯變更可能影響行為</summary>

原本 `isCurrentUser` 是 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示當 userIds 包含多個 ID 且其中包含當前使用者時，會被視為 current user，可能放寬權限檢查。請確認這是否符合預期。

**判斷依據**：diff 中修改的判斷式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:126</code> 測試檔案中 mock 的 Kysely 可能無法完全模擬實際行為</summary>

測試中使用了自訂的 mock Kysely，但實際的 Kysely 查詢鏈可能更複雜，導致測試無法捕捉到真實的錯誤。建議使用更貼近實際的 mock 或考慮整合測試。

**判斷依據**：diff 中新增的測試檔案，使用了簡化的 mock。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13723 (cache hit 12160) ｜ completion tokens 1688 ｜ PR #1</sub>