<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了團隊邀請連結的 API 端點（POST /v2/teams/:teamId/invite），包含控制器、模組、輸出 DTO 和端對端測試。主要風險在於權限控制：控制器使用 @Roles("TEAM_MEMBER")，但測試卻預期非管理員成員會收到 403，這表示角色裝飾器可能無法正確限制為僅管理員，或 TeamService.createInvite 內部的權限檢查與裝飾器不一致。此外，TeamService.createInvite 的變更將回傳的 token 從實際 token 改為 identifier，這可能破壞邀請連結的驗證流程，且 buildInviteLink 的條件判斷被反轉，可能導致非組織團隊取得錯誤的連結格式。建議優先修正權限邏輯與 token 回傳值，並補齊單元測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 權限控制不一致：@Roles("TEAM_MEMBER") 允許所有成員，但測試預期非管理員被拒 | 0.95 |
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 改為 identifier，可能破壞邀請驗證流程 | 0.90 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉，可能導致錯誤的邀請連結格式 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38` | 缺少輸入驗證：teamId 僅使用 ParseIntPipe，未檢查團隊是否存在或使用者權限 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:19` | 測試使用 Jest 語法，違反 R08（所有測試必須使用 Vitest） | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 權限控制不一致：@Roles("TEAM_MEMBER") 允許所有成員，但測試預期非管理員被拒</summary>

控制器使用 @Roles("TEAM_MEMBER") 來限制存取，但測試案例「should fail to create invite as non-admin member」預期非管理員成員會收到 403。這表示角色裝飾器可能無法正確限制為僅管理員，或 TeamService.createInvite 內部的權限檢查與裝飾器不一致。若實際部署，任何團隊成員都能建立邀請連結，可能導致未授權的邀請。建議確認 TeamService.createInvite 是否包含管理員檢查，並將裝飾器改為 @Roles("TEAM_ADMIN") 或移除裝飾器，完全依賴服務層的權限驗證。

**判斷依據**：diff 中控制器第 31 行顯示 @Roles("TEAM_MEMBER")，而測試檔案中明確有非管理員成員應失敗的案例。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 改為 identifier，可能破壞邀請驗證流程</summary>

原本回傳的是隨機產生的 token，現在改為回傳 newToken.identifier（即 `invite-link-for-teamId-${teamId}`）。邀請連結使用 token 參數，但驗證時可能預期收到隨機 token，而非 identifier。這會導致邀請連結無法通過驗證，或讓攻擊者能預測 identifier 而繞過邀請機制。建議回傳實際的 token，或確認驗證邏輯已同步更新。

**判斷依據**：diff 中將 return 物件的 token 從 token 改為 newToken.identifier。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉，可能導致錯誤的邀請連結格式</summary>

原本的條件是 `if (!isOrgContext)`，現在改為 `if (isOrgContext)`。這會讓非組織團隊取得組織專用的 getting started 連結，而組織團隊反而取得一般連結。這可能導致使用者被導向錯誤的頁面，或暴露不應公開的 onboarding 路徑。請確認此變更是否為預期行為，並修正條件。

**判斷依據**：diff 中將 `if (!isOrgContext)` 改為 `if (isOrgContext)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38</code> 缺少輸入驗證：teamId 僅使用 ParseIntPipe，未檢查團隊是否存在或使用者權限</summary>

控制器直接呼叫 TeamService.createInvite(teamId)，但未先驗證團隊是否存在或使用者是否有權限。若 teamId 不存在，服務層可能拋出未處理的錯誤，導致 500 回應。建議在服務層加入明確的錯誤處理，或使用全域例外過濾器。

**判斷依據**：控制器中直接呼叫服務，沒有錯誤處理或前置檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:19</code> 測試使用 Jest 語法，違反 R08（所有測試必須使用 Vitest）</summary>

測試檔案使用 Jest 風格的 describe、it、beforeAll、afterAll，但專案規範要求使用 Vitest。這可能導致測試無法在目前的測試環境中執行。建議將測試遷移至 Vitest 語法。

**判斷依據**：測試檔案開頭使用 describe，且未引入 Vitest 相關 import。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7147 (cache hit 7040) ｜ completion tokens 1352 ｜ PR #6</sub>