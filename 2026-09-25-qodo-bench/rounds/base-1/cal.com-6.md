<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點（POST /v2/teams/:teamId/invite），包含控制器、輸出 DTO、模組與端對端測試。主要風險在於 `TeamService.createInvite` 的變更：回傳的 token 改為 `newToken.identifier`，但 `identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token，這會導致回傳的 token 與邀請連結中的 token 不一致，且測試會失敗。此外，`buildInviteLink` 的條件判斷被反轉，可能造成非組織情境下產生錯誤的連結。權限控制使用 `@Roles("TEAM_MEMBER")`，但未驗證使用者是否為該團隊的成員，可能允許非成員建立邀請。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 不是實際邀請 token | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少團隊成員資格驗證 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:68` | 測試可能因 token 不一致而失敗 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 不是實際邀請 token</summary>

`createInvite` 回傳的 `token` 改為 `newToken.identifier`，但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位與 `inviteLink` 中的 token 不一致，且測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會失敗。應回傳 `token` 變數（即 `newToken.token`）或直接回傳 `token`。

**判斷依據**：diff 中將原本的 `token` 改為 `newToken.identifier`，而 `identifier` 在建立時設定為 `invite-link-for-teamId-${teamId}`，並非隨機 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉</summary>

原本的條件是 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會導致在非組織情境下，程式會繼續執行並呼叫 `OnboardingPathService.getGettingStartedPathWhenInvited`，可能產生錯誤的連結或非預期行為。應確認此變更是否為預期，否則應改回 `if (!isOrgContext)`。

**判斷依據**：diff 中將 `if (!isOrgContext)` 改為 `if (isOrgContext)`，但後續邏輯未變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少團隊成員資格驗證</summary>

控制器使用 `@Roles("TEAM_MEMBER")` 來限制角色，但未驗證使用者是否為該團隊的成員。任何具有 TEAM_MEMBER 角色的使用者（可能是其他團隊的成員）都可以對任意 teamId 建立邀請。應在服務層或控制器中加入團隊成員資格檢查，例如確認使用者與 teamId 的關聯。

**判斷依據**：控制器僅有角色裝飾器，沒有團隊成員資格檢查；且測試中非團隊成員的使用者預期會得到 403，但目前的實作可能無法達成。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:68</code> 測試可能因 token 不一致而失敗</summary>

測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會因為 token 回傳為 identifier 而失敗。此外，非管理員和非成員的測試預期 403，但若控制器未檢查團隊成員資格，這些測試可能不會通過。

**判斷依據**：測試依賴 token 與 inviteLink 的一致性，但服務層回傳的 token 有誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5718 (cache hit 1536) ｜ completion tokens 1114 ｜ PR #6</sub>