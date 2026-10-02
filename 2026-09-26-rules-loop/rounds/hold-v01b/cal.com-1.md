<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 bookings 查詢的權限判斷從「僅 ADMIN/OWNER 角色」改為「透過 PermissionCheckService 取得具有 booking.read 權限的團隊」，並在 repository 層加入 orgId 過濾。主要風險在於 SQL 查詢中 orgId 過濾條件的正確性、權限範圍變更可能導致的資料外洩或遺漏，以及測試覆蓋不足。建議優先確認 orgId 過濾邏輯與既有行為的相容性，並補齊邊界測試。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280` | orgId 過濾條件可能排除應包含的團隊 | 0.80 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309` | orgId 過濾條件在 UNION 分支中不一致 | 0.80 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:346` | orgId 過濾條件可能導致 fallback roles 結果不完整 | 0.80 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:357` | orgId 過濾條件在 fallback roles 的第二個 UNION 分支中不一致 | 0.80 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:117` | 權限範圍變更可能導致資料外洩或遺漏 | 0.75 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:149` | isCurrentUser 判斷邏輯變更可能影響行為 | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1` | 測試檔案缺少 orgId 相關測試 | 0.70 |
| 🔸 | Minor | `packages/features/pbac/infrastructure/repositories/__tests__/PermissionRepository.integration-test.ts:973` | 測試未涵蓋深層團隊階層 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280</code> orgId 過濾條件可能排除應包含的團隊</summary>

在 `getTeamsWithPBACPermissions` 的第一個 UNION 分支中，過濾條件為 `(t."id" = ${orgId} OR t."parentId" = ${orgId})`。這表示當 `orgId` 指定為某個組織 ID 時，只會回傳該組織本身及其直接子團隊。但若團隊階層超過兩層（例如組織 → 部門 → 子團隊），則更深層的子團隊將不會被包含。這可能導致使用者無法看到其應有權限的 bookings。

建議確認團隊階層的深度，若可能超過兩層，應改用遞迴 CTE 或調整過濾邏輯以包含所有後代團隊。

**判斷依據**：diff 中新增的 orgId 過濾條件僅檢查 t.id 或 t.parentId，未處理更深層的階層。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309</code> orgId 過濾條件在 UNION 分支中不一致</summary>

在 `getTeamsWithPBACPermissions` 的第二個 UNION 分支中，過濾條件為 `(org."id" = ${orgId} OR child."id" = ${orgId})`，但未包含 `child."parentId" = ${orgId}`。這可能導致當 `orgId` 指定為某個父團隊時，其子團隊不會被包含在結果中。

請確認此處的意圖，並與第一個分支的過濾邏輯保持一致。

**判斷依據**：diff 中第二個 UNION 分支的 orgId 過濾條件與第一個分支不同，缺少 child.parentId 的檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:346</code> orgId 過濾條件可能導致 fallback roles 結果不完整</summary>

在 `getTeamsWithFallbackRoles` 的第一個 UNION 分支中，過濾條件為 `(t."id" = ${orgId} OR t."parentId" = ${orgId})`，同樣只包含直接子團隊。若團隊階層超過兩層，則更深層的子團隊將不會被包含，可能導致使用者無法取得應有的 fallback 權限。

建議與 PBAC 查詢使用一致的階層處理邏輯。

**判斷依據**：diff 中 fallback roles 查詢的 orgId 過濾條件與 PBAC 查詢相同，但未處理深層階層。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:357</code> orgId 過濾條件在 fallback roles 的第二個 UNION 分支中不一致</summary>

在 `getTeamsWithFallbackRoles` 的第二個 UNION 分支中，過濾條件為 `(org."id" = ${orgId} OR child."id" = ${orgId} OR child."parentId" = ${orgId})`，但未包含 `org."parentId" = ${orgId}`。這可能導致當 `orgId` 指定為某個父團隊時，其子團隊不會被包含。

請確認此處的意圖，並與其他分支的過濾邏輯保持一致。

**判斷依據**：diff 中 fallback roles 查詢的第二個 UNION 分支過濾條件與其他分支不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:117</code> 權限範圍變更可能導致資料外洩或遺漏</summary>

原本的實作僅允許 ADMIN/OWNER 角色查看團隊成員的 bookings，現在改為使用 `PermissionCheckService.getTeamIdsWithPermission` 取得具有 `booking.read` 權限的團隊。這可能擴大或縮小可存取的範圍，取決於 PBAC 權限的設定。若某些團隊的 PBAC 權限設定不正確，可能導致使用者看到不應看到的 bookings，或看不到應有的 bookings。

建議確認此變更符合預期的權限模型，並進行充分的測試。

**判斷依據**：diff 中將原本的 membership 查詢替換為 PermissionCheckService 呼叫，權限判斷邏輯改變。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:149</code> isCurrentUser 判斷邏輯變更可能影響行為</summary>

原本的 `isCurrentUser` 判斷為 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示當 `userIds` 包含多個 ID 且其中包含當前使用者時，`isCurrentUser` 會是 true，可能導致後續的權限檢查邏輯改變。

請確認此變更是否符合預期，並確保不會造成權限繞過。

**判斷依據**：diff 中 isCurrentUser 的判斷條件從嚴格等於改為 includes。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1</code> 測試檔案缺少 orgId 相關測試</summary>

新增的測試檔案涵蓋了基本的權限檢查，但未測試 `orgId` 參數的傳遞與過濾行為。由於 repository 層的 orgId 過濾邏輯較複雜，建議在 handler 測試中加入 orgId 相關的測試案例，以確保行為正確。

**判斷依據**：測試檔案中未出現 orgId 相關的測試案例。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/pbac/infrastructure/repositories/__tests__/PermissionRepository.integration-test.ts:973</code> 測試未涵蓋深層團隊階層</summary>

新增的整合測試僅建立兩層團隊階層（組織 → 團隊），未測試更深層的階層。由於 orgId 過濾邏輯可能無法正確處理深層階層，建議加入三層以上的測試案例。

**判斷依據**：測試中建立的團隊階層僅有兩層。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13723 (cache hit 13696) ｜ completion tokens 2163 ｜ PR #1</sub>