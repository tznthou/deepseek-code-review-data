<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，並包含對應的 e2e 測試。主要風險在於 `TeamService.createInvite` 的變更：回傳值從 `token` 改為 `newToken.identifier`，但 `identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的 token，這會導致回傳的 token 不正確，且邀請連結仍使用正確的 token 建構，造成不一致。此外，`buildInviteLink` 的條件判斷被反轉，可能導致非組織團隊的邀請連結錯誤地包含額外的 onboarding 路徑。建議修正這兩個邏輯錯誤，並確認測試是否涵蓋這些情境。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 錯誤：使用 identifier 而非實際 token | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉，導致非組織團隊連結錯誤 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少使用者與團隊關係的授權檢查 | 0.85 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 錯誤：使用 identifier 而非實際 token</summary>

在 `createInvite` 中，原本回傳 `token`（隨機產生的 token），但變更後回傳 `newToken.identifier`。`identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位不正確，且與 `inviteLink` 中的 token 不一致。

**失敗情境**：當客戶端呼叫此端點取得邀請連結後，若使用回傳的 `token` 進行驗證，會因為 token 不正確而失敗。

**建議修法**：改回傳 `token`（即 `newToken.token`），或確認 `identifier` 的設計意圖，但根據目前程式碼，應回傳實際的 token。

**判斷依據**：diff 中將 `token` 改為 `newToken.identifier`，而 `identifier` 在建立時設定為 `invite-link-for-teamId-${teamId}`，與隨機產生的 `token` 不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉，導致非組織團隊連結錯誤</summary>

原本的條件是 `if (!isOrgContext)` 時直接回傳 `teamInviteLink`，否則加入 onboarding 路徑。變更後改為 `if (isOrgContext)` 直接回傳，這會讓非組織團隊（`isOrgContext` 為 false）的邀請連結錯誤地包含 onboarding 路徑，而組織團隊反而沒有。

**失敗情境**：非組織團隊的邀請連結會導向錯誤的 onboarding 流程，可能造成使用者體驗問題或功能異常。

**建議修法**：將條件改回 `if (!isOrgContext)`，或確認 `isOrgContext` 的語意是否已變更。

**判斷依據**：diff 中將 `if (!isOrgContext)` 改為 `if (isOrgContext)`，但後續邏輯未同步調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少使用者與團隊關係的授權檢查</summary>

控制器使用 `@Roles("TEAM_MEMBER")` 來限制角色，但未驗證目前使用者是否為該團隊的成員。`RolesGuard` 可能只檢查全域角色，而非針對特定團隊的成員資格。這可能允許任何具有 `TEAM_MEMBER` 角色的使用者為任意團隊建立邀請連結。

**失敗情境**：攻擊者若擁有 `TEAM_MEMBER` 角色（例如在其他團隊中），可以對任意 `teamId` 呼叫此端點，取得該團隊的邀請連結，進而加入未經授權的團隊。

**建議修法**：在服務層或控制器中加入團隊成員資格檢查，確認目前使用者是該團隊的成員（且可能需為管理員）。

**判斷依據**：控制器僅使用 `@Roles` 裝飾器，未見任何團隊成員資格驗證邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5682 (cache hit 5632) ｜ completion tokens 1089 ｜ PR #6</sub>