<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 booking 查詢的權限判斷從僅限 ADMIN/OWNER 改為使用 PBAC 權限系統，並新增 orgId 範圍過濾。主要風險在於 SQL 查詢中 orgId 的型別轉換與邏輯可能導致錯誤結果，且測試覆蓋不足。建議先修正 orgId 處理與查詢邏輯，再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280` | orgId 型別轉換可能導致 SQL 錯誤 | 0.90 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309` | orgId 過濾邏輯可能排除應包含的團隊 | 0.80 |
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280` | orgId 為 null 時的行為不一致 | 0.75 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:117` | 權限檢查失敗時可能導致資料外洩 | 0.70 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:149` | isCurrentUser 判斷邏輯變更可能導致權限繞過 | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1` | 測試覆蓋不足 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280</code> orgId 型別轉換可能導致 SQL 錯誤</summary>

在 SQL 查詢中使用 `${orgId}::bigint`，但 orgId 是 number | undefined。若 orgId 為 undefined，會產生 `undefined::bigint`，在 PostgreSQL 中會導致語法錯誤。應使用 Prisma 的參數化查詢或明確處理 undefined。

**判斷依據**：diff 中新增的 orgId 條件直接將參數嵌入 SQL 字串，未使用 Prisma 的參數綁定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309</code> orgId 過濾邏輯可能排除應包含的團隊</summary>

在 UNION 的第二部分，條件 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})` 只檢查 org.id 或 child.id 等於 orgId，但未考慮 child.parentId 等於 orgId 的情況。這可能導致當 orgId 為父組織時，子團隊被錯誤排除。

**判斷依據**：與第一部分相比，缺少 child."parentId" = ${orgId} 的條件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280</code> orgId 為 null 時的行為不一致</summary>

在 getTeamsWithPBACPermissions 中，orgId 參數型別為 number | null，但 SQL 條件使用 `${orgId}::bigint IS NULL`。若 orgId 為 null，會產生 `null::bigint`，在 PostgreSQL 中可能被視為 NULL，但行為依賴於資料庫。建議明確處理 null 與 undefined。

**判斷依據**：函式簽名允許 orgId 為 null，但 SQL 中未區分 null 與 undefined。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:117</code> 權限檢查失敗時可能導致資料外洩</summary>

getTeamIdsWithPermission 在發生錯誤時回傳空陣列，但呼叫端未檢查空陣列是否代表無權限或錯誤。若權限服務暫時故障，可能導致使用者看不到任何 booking，或更糟，若後續邏輯將空陣列視為無限制，可能造成資料外洩。建議明確區分錯誤與無權限。

**判斷依據**：PermissionCheckService.getTeamIdsWithPermission 的 catch 區塊回傳 []，但呼叫端未處理錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:149</code> isCurrentUser 判斷邏輯變更可能導致權限繞過</summary>

原本 isCurrentUser 僅在 filters.userIds 長度為 1 且等於 user.id 時為 true，現在改為 includes(user.id)。若 filters.userIds 包含多個 ID 且包含 user.id，則 isCurrentUser 為 true，可能允許使用者存取其他使用者的 booking。需確認此變更是否符合預期。

**判斷依據**：diff 中將原本的嚴格比較改為 includes。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:1</code> 測試覆蓋不足</summary>

新增的測試僅涵蓋基本情境，未測試 orgId 過濾、錯誤處理、以及 isCurrentUser 變更的影響。建議增加相關測試。

**判斷依據**：測試檔案中未包含 orgId 相關測試。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12284 (cache hit 1536) ｜ completion tokens 1374 ｜ PR #1</sub>