<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這次 PR 將 bookings 的權限檢查從僅限 ADMIN/OWNER 改為使用 PBAC 的 PermissionCheckService，並在 repository 層加入 orgId 過濾。整體方向合理，但測試檔案中大量使用 `as any` 與手動 mock，可能隱藏型別問題；且新增的測試檔案未遵循 R05 的 schema/handler 分離規範（雖然是測試檔，但 handler 本身已存在，此處僅測試）。主要風險在於測試的型別安全與 mock 的脆弱性，以及權限邏輯變更後是否完整覆蓋所有情境。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:8` | [R05] 測試檔案未遵循 schema/handler 分離模式 | 0.90 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:10` | 測試中使用大量 `as any` 與手動 mock，可能隱藏型別錯誤 | 0.80 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:121` | 權限邏輯變更可能遺漏對 `user.orgId` 的處理 | 0.70 |

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:8</code> [R05] 測試檔案未遵循 schema/handler 分離模式</summary>

新增的測試檔案 `get.handler.test.ts` 直接測試 handler，但 handler 本身應遵循 R05 的 schema/handler 分離。雖然此檔案是測試，但若 handler 未正確使用 schema 驗證，測試可能無法捕捉到型別錯誤。建議確認 handler 已使用對應的 Zod schema，並在測試中驗證輸入驗證行為。

**判斷依據**：diff 中新增了測試檔案，直接 import handler，但未見 schema 相關測試。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:10</code> 測試中使用大量 `as any` 與手動 mock，可能隱藏型別錯誤</summary>

測試中多處使用 `as any`（例如 `mockBookings`、`mockUser as any`、`mockPrisma` 等），且手動建立複雜的 mock 物件（如 `createMockKysely`）。這會降低測試的型別安全性，且當實際介面變更時，測試可能不會失敗，導致錯誤未被發現。建議使用更嚴格的型別或依賴測試輔助工具來建立 mock。

**判斷依據**：diff 中多處出現 `as any` 與手動 mock 建構。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:121</code> 權限邏輯變更可能遺漏對 `user.orgId` 的處理</summary>

原本的邏輯會根據 `user.orgId` 限制查詢範圍（僅限組織內），但新的 `getTeamIdsWithPermission` 呼叫傳入了 `orgId: user.orgId ?? undefined`，若 `user.orgId` 為 null，則不限制範圍。這可能導致非組織用戶取得過多權限。建議確認此行為是否符合預期，並在測試中涵蓋 `user.orgId` 為 null 的情境。

**判斷依據**：diff 中新增了 `orgId` 參數傳遞，但未見對 null 情況的明確處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13760 (cache hit 13696) ｜ completion tokens 844 ｜ PR #1</sub>