<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 bookings 查詢的權限判斷從「僅 ADMIN/OWNER 角色」改為「透過 PermissionCheckService 檢查 booking.read 權限」，並在 PBAC repository 中新增 orgId 參數以支援組織範圍過濾。主要風險在於 SQL 查詢中 orgId 的型別轉換可能導致效能問題，以及測試中 mock 的實作可能無法正確模擬實際行為。建議先確認 orgId 的型別與索引使用情況，並補強測試的可靠性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280` | orgId 型別轉換可能導致索引失效 | 0.80 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:128` | 測試中的 mock 可能無法正確模擬實際查詢 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280</code> orgId 型別轉換可能導致索引失效</summary>

在 SQL 查詢中使用 `${orgId}::bigint` 進行比較，若 orgId 為 number 型別，Prisma 會將其參數化為 integer，但資料庫中的 id 欄位可能是 bigint，導致型別不匹配而無法使用索引。建議確認 orgId 的實際型別，並避免不必要的型別轉換，或使用 Prisma 的型別安全參數化方式。

**判斷依據**：diff 中新增的 orgId 過濾條件使用了 `::bigint` 轉型，但未確認 orgId 的原始型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:128</code> 測試中的 mock 可能無法正確模擬實際查詢</summary>

在 `createMockKysely` 中，`select` 方法在收到 callback 時直接回傳 `mockQueryBuilder`，但實際 Kysely 的 callback 會接收一個 query builder 並回傳新的 builder，此 mock 可能導致測試無法涵蓋真實的查詢邏輯。建議使用更貼近實際行為的 mock 或改用整合測試。

**判斷依據**：測試中 mock 的 select 方法未正確處理 callback，可能導致測試通過但實際行為錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12248 (cache hit 12160) ｜ completion tokens 645 ｜ PR #1</sub>