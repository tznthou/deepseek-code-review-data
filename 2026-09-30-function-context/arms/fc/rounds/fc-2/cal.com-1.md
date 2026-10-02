<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將取得預約列表的權限檢查從「僅 ADMIN/OWNER 角色」改為「透過 PBAC 的 booking.read 權限或 fallback 角色」，並在 repository 層加入 orgId 過濾。整體方向合理，但存在幾個需要修正的問題：getTeamIdsWithPermission 未將 orgId 傳遞給 getTeamIdsWithPermissions，導致 orgId 過濾失效；getBookings 中 userIds 過濾的自我存取判斷從「僅限單一 ID」改為「包含自身 ID」，可能造成權限繞過；此外，測試中對 PermissionCheckService 的 mock 未涵蓋 orgId 參數，且部分測試的 mock 設定可能不完整。建議優先修正 orgId 傳遞與 userIds 過濾邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:222` | getTeamIdsWithPermission 未傳遞 orgId，導致 orgId 過濾失效 | 0.95 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/bookings/get.handler.ts:149` | userIds 過濾的自我存取判斷從「僅限單一 ID」改為「包含自身 ID」，可能造成權限繞過 | 0.80 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:127` | 測試中 mock 的 PermissionCheckService 未涵蓋 orgId 參數 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:222</code> getTeamIdsWithPermission 未傳遞 orgId，導致 orgId 過濾失效</summary>

在 `getTeamIdsWithPermission` 方法中，呼叫 `this.getTeamIdsWithPermissions` 時未將 `orgId` 參數傳入。這會導致當呼叫端使用 `getTeamIdsWithPermission` 並提供 `orgId` 時，該過濾條件不會被套用，可能回傳不屬於該組織的團隊 ID，造成權限檢查不正確。

**失敗情境**：使用者呼叫 `getTeamIdsWithPermission({ userId, permission, fallbackRoles, orgId: 123 })`，但回傳的團隊 ID 包含不屬於 org 123 的團隊。

**建議修法**：將 `orgId` 加入傳遞物件：
```typescript
return this.getTeamIdsWithPermissions({ userId, permissions: [permission], fallbackRoles, orgId });
```

**判斷依據**：diff 中 `getTeamIdsWithPermission` 方法新增了 `orgId` 參數，但呼叫 `getTeamIdsWithPermissions` 時未包含 `orgId`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.ts:149</code> userIds 過濾的自我存取判斷從「僅限單一 ID」改為「包含自身 ID」，可能造成權限繞過</summary>

原本的判斷是 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示當 `filters.userIds` 包含多個 ID 且其中包含當前使用者 ID 時，即使其他 ID 不在可存取範圍內，也不會觸發 FORBIDDEN 錯誤。

**失敗情境**：攻擊者提供 `userIds: [自己的ID, 受害者的ID]`，由於包含自己的 ID，`isCurrentUser` 為 true，因此不會檢查其他 ID 是否在可存取範圍內，可能導致越權存取。

**建議修法**：保留原本的嚴格判斷，或改為檢查所有 ID 是否都在可存取範圍內，且僅當 `filters.userIds` 只包含當前使用者 ID 時才視為自我存取。

**判斷依據**：diff 中此行取代了原本的 `const isCurrentUser = filters.userIds.length === 1 && user.id === filters.userIds[0];`

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/get.handler.test.ts:127</code> 測試中 mock 的 PermissionCheckService 未涵蓋 orgId 參數</summary>

在測試中，`mockGetTeamIdsWithPermission` 被設定為 `vi.fn()`，但沒有驗證呼叫時是否傳遞了 `orgId`。由於 handler 中會將 `user.orgId` 傳入 `getTeamIdsWithPermission`，測試應確認此參數被正確傳遞，以確保 orgId 過濾邏輯有被測試覆蓋。

**建議修法**：在相關測試中加入對 `orgId` 的斷言，例如：
```typescript
expect(mockGetTeamIdsWithPermission).toHaveBeenCalledWith({
  userId: 1,
  permission: "booking.read",
  fallbackRoles: ["ADMIN", "OWNER"],
  orgId: null, // 或實際的 orgId
});
```

**判斷依據**：測試中對 `mockGetTeamIdsWithPermission` 的斷言未包含 `orgId`，而 handler 程式碼會傳遞 `orgId`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 27964 (cache hit 27904) ｜ completion tokens 1277 ｜ PR #1</sub>