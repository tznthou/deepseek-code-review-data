<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，包含控制器、輸出 DTO、模組與端對端測試。主要風險在於 `TeamService.createInvite` 的回傳值變更：原本回傳 token，現在改回傳 `newToken.identifier`，這會導致回傳的 token 與實際建立的 verificationToken 不一致，且 `buildInviteLink` 的條件判斷被反轉，可能產生錯誤的邀請連結。此外，控制器使用 `@Roles("TEAM_MEMBER")` 但測試預期非管理員成員應被拒絕，權限設定可能過於寬鬆。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 與實際建立的 verificationToken 不一致 | 0.95 |
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉，導致邀請連結錯誤 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 權限設定過於寬鬆：TEAM_MEMBER 即可建立邀請，但測試預期非管理員應被拒絕 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38` | 缺少對 teamId 的擁有權或存在性檢查 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 與實際建立的 verificationToken 不一致</summary>

`createInvite` 原本回傳 `token`（隨機產生的 token），現在改為回傳 `newToken.identifier`。但 `identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的 token。這會導致 API 回傳的 token 無法用於驗證邀請，且與 `inviteLink` 中的 token 不一致。

失敗情境：使用者取得邀請連結後，使用連結中的 token 進行驗證，但資料庫中的 verificationToken 的 token 欄位是隨機產生的 token，而 identifier 是固定格式，因此驗證會失敗。

建議：回傳 `token` 而非 `newToken.identifier`。

**判斷依據**：diff 中將原本的 `token,` 改為 `token: newToken.identifier,`，而 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位是 `invite-link-for-teamId-${teamId}`，不是隨機 token。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉，導致邀請連結錯誤</summary>

原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，現在改為 `if (isOrgContext) { return teamInviteLink; }`。這會使得在組織情境下（isOrgContext 為 true）直接回傳 teamInviteLink，而沒有附加 getting started 路徑；反之在非組織情境下卻會附加 getting started 路徑。

失敗情境：組織團隊的邀請連結缺少必要的 onboarding 參數，使用者點擊後可能無法正確導向。

建議：恢復原本的條件判斷，或確認邏輯是否應為 `if (isOrgContext) { ... } else { return teamInviteLink; }`。

**判斷依據**：diff 中將 `if (!isOrgContext)` 改為 `if (isOrgContext)`，且後續程式碼仍使用 `isOrgContext` 來決定是否附加 getting started 路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 權限設定過於寬鬆：TEAM_MEMBER 即可建立邀請，但測試預期非管理員應被拒絕</summary>

控制器使用 `@Roles("TEAM_MEMBER")`，這表示任何團隊成員（包括 MEMBER）都可以呼叫此端點。然而，端對端測試中明確預期非管理員成員應收到 403。這可能導致權限提升漏洞：一般成員可以建立邀請連結，進而邀請他人加入團隊。

失敗情境：一個非管理員的團隊成員呼叫此 API，成功建立邀請連結，違反了團隊管理員的權限控制。

建議：將角色改為 `TEAM_ADMIN` 或更嚴格的權限，並確認測試與實作一致。

**判斷依據**：控制器使用 `@Roles("TEAM_MEMBER")`，但測試檔案中 `should fail to create invite as non-admin member` 預期 403。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38</code> 缺少對 teamId 的擁有權或存在性檢查</summary>

控制器直接呼叫 `TeamService.createInvite(teamId)`，但沒有先驗證目前使用者是否屬於該團隊或團隊是否存在。雖然有 RolesGuard，但 RolesGuard 可能只檢查全域角色，而非針對特定團隊的成員資格。

失敗情境：使用者可能對任意 teamId 建立邀請，即使不是該團隊成員。

建議：在服務層或控制器中加入團隊成員資格檢查。

**判斷依據**：控制器中沒有對 teamId 進行任何授權檢查，僅依賴全域的 RolesGuard。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5718 (cache hit 5632) ｜ completion tokens 1322 ｜ PR #6</sub>