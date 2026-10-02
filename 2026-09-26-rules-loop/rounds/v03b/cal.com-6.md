<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了團隊邀請連結的 API 端點（POST /v2/teams/:teamId/invite），包含控制器、輸出 DTO、模組註冊與 E2E 測試。主要風險在於權限控制：控制器使用 @Roles("TEAM_MEMBER")，但測試卻預期非管理員成員會被拒絕（403），這表示角色檢查可能不足，任何團隊成員都能建立邀請連結，而這原本應是管理員功能。此外，TeamService.createInvite 的回傳值有變更（token 改為 newToken.identifier），但 identifier 欄位可能不是預期的 token 值，需要確認。還有一些次要問題，例如缺少新檔案的換行符、測試未使用 UTC 時區設定（違反 R08）、以及未處理的錯誤路徑。建議先修正權限檢查邏輯，確保只有管理員能建立邀請連結。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 權限控制不足：任何團隊成員都能建立邀請連結 | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 可能不是實際的邀請 token | 0.80 |
| 🔸 | Minor | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 的條件判斷可能相反 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1` | [R08] 測試未使用 Vitest 框架 | 0.70 |
| 🔸 | Minor | `packages/features/ee/teams/services/teamService.ts:567` | 檔案結尾缺少換行符 | 0.60 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1` | 測試未設定 UTC 時區 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 權限控制不足：任何團隊成員都能建立邀請連結</summary>

控制器使用 @Roles("TEAM_MEMBER")，但測試中明確預期非管理員成員會被拒絕（403）。這表示角色檢查可能只驗證使用者是否為團隊成員，而未驗證是否為管理員。邀請連結通常應僅限管理員建立，否則任何成員都能邀請外部人員加入團隊，造成安全風險。

建議：將角色改為 @Roles("TEAM_ADMIN") 或類似角色，並確認 RolesGuard 能正確檢查團隊層級的管理員權限。

**判斷依據**：測試檔案 teams-invite.controller.e2e-spec.ts 中，非管理員成員的測試預期 403，但控制器只要求 TEAM_MEMBER 角色。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 可能不是實際的邀請 token</summary>

原本回傳的 token 是隨機產生的 token，但現在改為 newToken.identifier。identifier 欄位在建立時設定為 `invite-link-for-teamId-${teamId}`，這不是隨機 token，而是固定的識別字串。這可能導致回傳給客戶端的 token 不是實際用於驗證的 token，造成邀請連結失效或安全問題。

建議：確認 verificationToken 的結構，回傳正確的 token 欄位（應為 newToken.token），而不是 identifier。

**判斷依據**：diff 中原本是 token，現在改為 newToken.identifier，而 identifier 在建立時是固定字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 的條件判斷可能相反</summary>

原本的條件是 if (!isOrgContext) 回傳 teamInviteLink，現在改為 if (isOrgContext) 回傳 teamInviteLink。這可能導致非組織情境下反而回傳了組織專用的連結，或反之。需要確認 isOrgContext 的語意與預期行為。

**判斷依據**：diff 中條件從 !isOrgContext 改為 isOrgContext，但未提供說明。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1</code> [R08] 測試未使用 Vitest 框架</summary>

測試檔案使用 Jest 風格的 describe/it/expect，但專案規範 R08 要求所有測試使用 Vitest。這可能導致測試無法在 CI 中正確執行。建議改用 Vitest 的 API（例如從 'vitest' 匯入 describe, it, expect）。

**判斷依據**：整個測試檔案使用 Jest 語法，且未匯入 Vitest。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/ee/teams/services/teamService.ts:567</code> 檔案結尾缺少換行符</summary>

檔案結尾缺少換行符，可能違反專案的格式化規範（R03）。建議在最後一行加上換行。

**判斷依據**：diff 顯示最後一行沒有換行符（\ No newline at end of file）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1</code> 測試未設定 UTC 時區</summary>

專案規範 R08 要求測試命令設定 TZ=UTC，但此測試檔案未明確設定時區。若測試涉及時間相關邏輯，可能在不同時區下失敗。建議在測試配置中設定 TZ=UTC。

**判斷依據**：測試檔案中沒有設定時區的程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7167 (cache hit 7040) ｜ completion tokens 1411 ｜ PR #6</sub>