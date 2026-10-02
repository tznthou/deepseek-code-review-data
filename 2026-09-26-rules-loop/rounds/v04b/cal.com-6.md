<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了團隊邀請連結的 API 端點，包含 controller、DTO、module 與 e2e 測試。主要風險在於 `TeamService.createInvite` 的回傳值被改為 `newToken.identifier`，這會讓 API 回傳的 token 變成固定字串 `invite-link-for-teamId-{teamId}`，而不是實際的隨機 token，導致邀請連結失效。此外，`buildInviteLink` 的條件判斷被反轉，可能造成非組織團隊拿到錯誤的連結格式。建議先修正這兩個邏輯錯誤，再考慮合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 是 identifier 而非隨機 token，導致邀請連結失效 | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 的條件判斷反轉，可能產生錯誤的邀請連結 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少 teamId 的權限檢查，任何 team member 都能為任意 team 建立邀請 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:29` | 測試使用隨機 email，可能造成測試資料殘留 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 是 identifier 而非隨機 token，導致邀請連結失效</summary>

`createInvite` 原本回傳 `token`（隨機產生的 64 字元 hex），現在改成回傳 `newToken.identifier`。但 `identifier` 是固定格式 `invite-link-for-teamId-${teamId}`，並非隨機值。這會讓 API 回傳的 `token` 欄位變成可預測的字串，且 `inviteLink` 中的 token 參數仍使用原始的隨機 token，兩者不一致，導致邀請連結無法使用。

**失敗情境**：呼叫 `POST /v2/teams/:teamId/invite` 後，回應中的 `data.token` 會是 `invite-link-for-teamId-123`，而 `data.inviteLink` 中的 `token` 參數是隨機 hex。使用者點擊連結後，系統會用隨機 hex 查詢資料庫，但資料庫中儲存的 token 是隨機 hex，而 identifier 是固定字串，因此驗證會失敗。

**建議**：改回回傳 `token`（隨機值），不要回傳 `identifier`。

**判斷依據**：diff 中 `-    await prisma.verificationToken.create({` 改為 `+    const newToken = await prisma.verificationToken.create({`，且回傳物件中 `-      token,` 改為 `+      token: newToken.identifier,`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 的條件判斷反轉，可能產生錯誤的邀請連結</summary>

原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，代表非組織情境直接回傳基本連結；組織情境則會加上 getting started 路徑。現在改成 `if (isOrgContext) { return teamInviteLink; }`，變成組織情境回傳基本連結，非組織情境反而會執行後面的 getting started 邏輯。這與預期行為相反，可能導致非組織團隊的邀請連結帶有錯誤的 callback 路徑。

**失敗情境**：當 `isOrgContext` 為 `false`（非組織團隊）時，程式會進入 `OnboardingPathService.getGettingStartedPathWhenInvited` 並產生帶有 `callbackUrl=/getting-started` 的連結，但這可能不是非組織團隊想要的行為。

**建議**：將條件改回 `if (!isOrgContext) { return teamInviteLink; }`。

**判斷依據**：diff 中 `-    if (!isOrgContext) {` 改為 `+    if (isOrgContext) {`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少 teamId 的權限檢查，任何 team member 都能為任意 team 建立邀請</summary>

Controller 使用 `@Roles("TEAM_MEMBER")` 來限制只有 team member 可以呼叫，但沒有驗證目前使用者是否屬於 `:teamId` 指定的團隊。這表示任何已驗證的使用者（具有 TEAM_MEMBER 角色）都可以為任意 teamId 建立邀請連結，只要他們知道該 teamId。

**失敗情境**：攻擊者取得一個有效的 API key（即使是某個團隊的 member），然後呼叫 `POST /v2/teams/999/invite`，就能為 team 999 建立邀請連結，進而取得加入該團隊的權限。

**建議**：在 controller 或 service 中加入檢查，確認目前使用者是該 team 的 member（且可能是 admin）才能建立邀請。

**判斷依據**：diff 中新增的 controller 只有 `@Roles("TEAM_MEMBER")`，沒有其他權限檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:29</code> 測試使用隨機 email，可能造成測試資料殘留</summary>

測試中使用 `randomString()` 產生唯一的 email，但 `afterAll` 只刪除了 user 和 team，沒有刪除 membership。這可能導致測試資料殘留在資料庫中，影響後續測試或造成資料污染。

**失敗情境**：如果測試中途失敗，`afterAll` 可能不會執行，導致測試資料永久殘留。

**建議**：使用 transaction 或確保在 `afterAll` 中刪除所有相關資料，包括 membership。

**判斷依據**：diff 中新增的測試檔案，`afterAll` 只刪除 user 和 team，沒有刪除 membership。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6342 (cache hit 6272) ｜ completion tokens 1487 ｜ PR #6</sub>