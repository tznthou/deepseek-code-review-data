<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點（POST /v2/teams/:teamId/invite），包含控制器、DTO、模組與 E2E 測試。主要風險在於 `TeamService.createInvite` 的回傳值變更：原本回傳 token，現在改為回傳 `newToken.identifier`（即 `invite-link-for-teamId-${teamId}`），這會導致回傳的 token 不再是實際的邀請 token，而是 identifier，且 `buildInviteLink` 的條件判斷也反轉了，可能造成邀請連結錯誤。此外，控制器使用 `@Roles("TEAM_MEMBER")` 但測試期望非管理員成員應被拒絕（403），這可能表示角色檢查邏輯有誤或測試與實作不一致。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 改為 identifier，導致邀請 token 錯誤 | 0.95 |
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 的條件判斷反轉，導致邀請連結錯誤 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 角色裝飾器使用 TEAM_MEMBER，但測試期望非管理員被拒絕 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38` | 缺少對 teamId 的權限檢查 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 改為 identifier，導致邀請 token 錯誤</summary>

原本回傳 `token`（隨機產生的邀請 token），現在改為 `newToken.identifier`（即 `invite-link-for-teamId-${teamId}`）。這會讓 API 回傳的 `token` 欄位不再是實際的邀請 token，而是 identifier，導致客戶端使用此 token 時無法正確加入團隊。

失敗情境：呼叫 `POST /v2/teams/:teamId/invite` 後，回應中的 `data.token` 會是 `invite-link-for-teamId-123`，而非隨機 token。若客戶端將此值用於邀請連結或驗證，將無法運作。

建議：應回傳 `newToken.token`（實際的隨機 token），而不是 `newToken.identifier`。

**判斷依據**：diff 中 `token: newToken.identifier,` 取代了原本的 `token,`，而 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位是 `invite-link-for-teamId-${teamId}`，並非隨機 token。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 的條件判斷反轉，導致邀請連結錯誤</summary>

原本 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會讓非組織情境（一般團隊）的邀請連結變成 `/teams?token=...`，而組織情境反而會進入後續的 getting started 路徑，與預期相反。

失敗情境：當 `isOrgContext` 為 false（一般團隊）時，原本應回傳包含 getting started 路徑的連結，現在卻回傳 `/teams?token=...`，導致使用者點擊後無法正確導向。

建議：應改回 `if (!isOrgContext)` 或確認邏輯是否正確。

**判斷依據**：diff 中 `if (!isOrgContext)` 改為 `if (isOrgContext)`，但後續的 getting started 路徑應在非組織情境下使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 角色裝飾器使用 TEAM_MEMBER，但測試期望非管理員被拒絕</summary>

控制器使用 `@Roles("TEAM_MEMBER")`，這表示任何團隊成員（包括 MEMBER）都可以呼叫此端點。但 E2E 測試中，非管理員成員（role: MEMBER）預期會收到 403。這可能表示角色檢查邏輯有誤，或測試與實作不一致。

失敗情境：若實際部署後，非管理員成員可以成功建立邀請連結，則可能違反權限設計。

建議：確認此端點應允許哪些角色。若僅允許管理員，應改為 `@Roles("TEAM_ADMIN")` 或類似角色；若允許所有成員，則測試應調整為預期 200。

**判斷依據**：控制器使用 `@Roles("TEAM_MEMBER")`，而測試檔案中 `should fail to create invite as non-admin member` 預期 403。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38</code> 缺少對 teamId 的權限檢查</summary>

控制器直接呼叫 `TeamService.createInvite(teamId)`，但未檢查目前使用者是否為該團隊的成員或管理員。雖然有 `RolesGuard`，但 `@Roles("TEAM_MEMBER")` 可能只檢查全域角色，而非針對特定團隊的成員資格。

失敗情境：若使用者是某個團隊的成員，但嘗試對另一個團隊的 `teamId` 建立邀請，可能成功（若角色檢查僅基於全域角色）。

建議：在服務層或控制器中加入團隊成員資格驗證，確保使用者有權限對該團隊進行操作。

**判斷依據**：控制器未使用 `@GetUser()` 取得使用者資訊，也未傳遞使用者 ID 給服務層進行權限驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5718 (cache hit 5632) ｜ completion tokens 1410 ｜ PR #6</sub>