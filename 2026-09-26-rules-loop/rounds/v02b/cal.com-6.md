<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，包含控制器、輸出 DTO、模組與測試。主要風險在於 `TeamService.createInvite` 的變更：回傳的 token 改為 `newToken.identifier`，但 identifier 是固定字串而非隨機 token，導致邀請連結失效；同時 `buildInviteLink` 的條件判斷被反轉，可能造成非組織團隊的連結錯誤。此外，控制器缺少使用者與團隊關係的權限檢查，任何通過驗證的使用者都可能為任意團隊建立邀請。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 使用錯誤欄位，導致邀請連結失效 | 0.95 |
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉，導致非組織團隊連結錯誤 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少使用者與團隊關係的權限檢查 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38` | 缺少輸入驗證與錯誤處理 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 使用錯誤欄位，導致邀請連結失效</summary>

在 `createInvite` 方法中，原本回傳的 `token` 是隨機產生的 `token` 變數，但修改後改為 `newToken.identifier`。`identifier` 是 `invite-link-for-teamId-${teamId}` 這個固定字串，並非隨機 token。這會導致回傳給使用者的 token 不正確，邀請連結中的 token 也無法用於驗證，造成邀請功能完全失效。

建議改回回傳 `token` 變數，或確認 `newToken` 中哪個欄位才是實際的隨機 token。

**判斷依據**：diff 中 `-    return {\n-      token,\n+    return {\n+      token: newToken.identifier,` 顯示原本回傳 `token`，現在改為 `newToken.identifier`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉，導致非組織團隊連結錯誤</summary>

`buildInviteLink` 方法中，原本的條件是 `if (!isOrgContext)`，現在改為 `if (isOrgContext)`。這會導致當 `isOrgContext` 為 `false`（非組織團隊）時，程式碼會進入 `else` 分支，呼叫 `OnboardingPathService.getGettingStartedPathWhenInvited` 並回傳帶有 `callbackUrl` 的連結；而當 `isOrgContext` 為 `true` 時，反而回傳簡單的團隊邀請連結。這與預期行為相反，可能造成非組織團隊的邀請連結包含錯誤的 callback URL。

建議將條件改回 `if (!isOrgContext)`。

**判斷依據**：diff 中 `-    if (!isOrgContext) {\n+    if (isOrgContext) {` 顯示條件被反轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少使用者與團隊關係的權限檢查</summary>

控制器使用 `@Roles("TEAM_MEMBER")` 裝飾器，但這只檢查使用者的全域角色，並未驗證使用者是否屬於該團隊或具有管理員權限。任何通過驗證的使用者（即使不是團隊成員）都可以呼叫此端點為任意團隊建立邀請連結，造成權限繞過。

建議在服務層或控制器中加入團隊成員資格檢查，例如確認使用者是否為該團隊的 ADMIN 或 MEMBER。

**判斷依據**：控制器中只有 `@Roles("TEAM_MEMBER")`，沒有針對 `teamId` 的成員資格檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38</code> 缺少輸入驗證與錯誤處理</summary>

控制器直接呼叫 `TeamService.createInvite(teamId)`，沒有對 `teamId` 進行存在性檢查或錯誤處理。如果 `teamId` 不存在，服務層可能會拋出未處理的例外，導致 500 錯誤。建議加入適當的錯誤處理或使用全域例外過濾器。

**判斷依據**：控制器方法中沒有 try-catch 或錯誤處理邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7157 (cache hit 7040) ｜ completion tokens 1149 ｜ PR #6</sub>