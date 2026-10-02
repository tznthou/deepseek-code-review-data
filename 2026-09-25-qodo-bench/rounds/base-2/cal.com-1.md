<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將預訂查詢的權限檢查從僅限 ADMIN/OWNER 角色改為使用 PBAC 權限系統，並新增 orgId 範圍過濾。主要風險在於 SQL 查詢中 orgId 的型別轉換可能導致效能問題、權限邏輯變更可能造成資料外洩或功能回歸，以及測試覆蓋不足。建議優先修正 SQL 型別轉換與驗證 orgId 的來源，並補充整合測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280` | orgId 型別轉換可能導致索引失效與全表掃描 | 0.85 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:117` | 權限邏輯變更可能導致資料外洩或功能回歸 | 0.80 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:149` | isCurrentUser 判斷邏輯變更可能導致權限繞過 | 0.75 |
| 🔸 | Minor | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:222` | getTeamIdsWithPermission 未傳遞 orgId 參數 | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1` | 測試覆蓋不足，未涵蓋 orgId 過濾與權限邊界案例 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280</code> orgId 型別轉換可能導致索引失效與全表掃描</summary>

在 SQL 查詢中使用 `${orgId}::bigint` 進行型別轉換，可能導致資料庫無法使用 Team.id 上的索引，造成全表掃描。當 orgId 為 null 時，條件 `(${orgId}::bigint IS NULL OR ...)` 會使整個條件恆真，但資料庫仍可能對 Team 表進行全表掃描。建議改為在應用程式層處理 null 情況，例如使用條件式查詢或將 orgId 作為參數傳遞，避免在 SQL 中進行型別轉換。

**判斷依據**：diff 中新增的條件 `AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})` 直接將 orgId 轉換為 bigint，可能影響查詢效能。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:117</code> 權限邏輯變更可能導致資料外洩或功能回歸</summary>

原本僅 ADMIN/OWNER 角色可查看的預訂，現在改為任何具有 booking.read 權限的使用者皆可查看。若 PBAC 權限設定不當，可能導致未授權使用者存取他人預訂資料。此外，若 PermissionCheckService 回傳空陣列，則所有查詢分支都會被跳過，可能導致使用者看不到自己的預訂。建議確認 booking.read 權限的預設設定，並確保使用者至少能查看自己的預訂。

**判斷依據**：diff 中移除了原本的 membershipIdsWhereUserIsAdminOwner 查詢，改為使用 PermissionCheckService，權限範圍可能擴大。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:149</code> isCurrentUser 判斷邏輯變更可能導致權限繞過</summary>

原本 `isCurrentUser` 僅在 `filters.userIds.length === 1 && user.id === filters.userIds[0]` 時為 true，現在改為 `filters.userIds.includes(user.id)`。這表示若 userIds 陣列包含目前使用者 ID 及其他使用者 ID，則 `isCurrentUser` 會為 true，可能繞過後續的權限檢查。建議確認此變更是否符合預期，並確保不會造成未授權存取。

**判斷依據**：diff 中將 `isCurrentUser` 的判斷從嚴格相等改為 includes，可能影響權限檢查邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:222</code> getTeamIdsWithPermission 未傳遞 orgId 參數</summary>

在 `getTeamIdsWithPermission` 方法中，呼叫 `this.getTeamIdsWithPermissions` 時未傳遞 `orgId` 參數，導致 orgId 過濾功能在單一權限查詢中失效。建議補上 `orgId` 參數。

**判斷依據**：diff 中 `getTeamIdsWithPermission` 方法新增了 orgId 參數，但呼叫 `getTeamIdsWithPermissions` 時未傳遞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1</code> 測試覆蓋不足，未涵蓋 orgId 過濾與權限邊界案例</summary>

新增的測試僅涵蓋基本成功案例與部分權限檢查，未測試 orgId 過濾功能、空權限陣列、無權限使用者等邊界情況。建議補充相關測試以確保功能正確性。

**判斷依據**：diff 中新增的測試檔案僅包含少數測試案例，未涵蓋所有新增功能。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12284 (cache hit 12160) ｜ completion tokens 1390 ｜ PR #1</sub>