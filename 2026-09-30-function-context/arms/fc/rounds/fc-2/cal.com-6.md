<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，包含控制器、模組、輸出 DTO 與 e2e 測試。主要風險在於 `TeamService.createInvite` 的回傳值錯誤：回傳了 `identifier` 而非 `token`，導致邀請連結中的 token 與回傳的 token 不一致，且無法用於後續驗證。此外，`buildInviteLink` 的條件判斷邏輯被反轉，可能造成非組織團隊的邀請連結導向錯誤頁面。建議優先修正這兩個問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | createInvite 回傳錯誤的 token 欄位 | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷邏輯反轉 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少團隊成員權限驗證 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:78` | 測試未驗證邀請連結的正確性 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> createInvite 回傳錯誤的 token 欄位</summary>

在 `createInvite` 方法中，建立新的 verification token 後，回傳物件使用了 `newToken.identifier` 而非 `newToken.token`。這會導致 API 回應中的 `token` 欄位是 `invite-link-for-teamId-<teamId>` 而非實際的隨機 token，而 `inviteLink` 中使用的 token 是正確的隨機 token。這造成兩個問題：
1. 客戶端拿到的 `token` 與 `inviteLink` 中的 token 不一致，無法用於驗證。
2. 若客戶端使用回傳的 `token` 進行邀請驗證，將永遠失敗。

**建議修正**：將回傳的 `token` 改為 `newToken.token`。

**判斷依據**：diff 中顯示 `-    await prisma.verificationToken.create({` 改為 `+    const newToken = await prisma.verificationToken.create({`，且回傳物件從 `-      token,` 改為 `+      token: newToken.identifier,`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷邏輯反轉</summary>

在 `buildInviteLink` 方法中，原本的條件 `if (!isOrgContext)` 被改為 `if (isOrgContext)`，這導致當 `isOrgContext` 為 true（組織或組織中的團隊）時，回傳的是 `teamInviteLink`（`/teams?token=...`），而當 `isOrgContext` 為 false（一般團隊）時，回傳的是 `orgInviteLink`（`/signup?token=...&callbackUrl=...`）。這與預期行為相反：一般團隊應該使用 `/teams` 連結，組織應該使用 `/signup` 連結。

**建議修正**：將條件改回 `if (!isOrgContext)`。

**判斷依據**：diff 中顯示 `-    if (!isOrgContext) {` 改為 `+    if (isOrgContext) {`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少團隊成員權限驗證</summary>

控制器使用 `@Roles("TEAM_MEMBER")` 裝飾器，但 `RolesGuard` 的實作可能只檢查使用者的全域角色，而非其在特定團隊中的角色。這可能導致任何具有 `TEAM_MEMBER` 角色的使用者都能為任意團隊建立邀請連結，即使他們不是該團隊的成員。需要確認 `RolesGuard` 是否支援團隊層級的權限檢查，若無，則應在服務層或控制器中加入團隊成員驗證。

**判斷依據**：控制器中僅有 `@Roles("TEAM_MEMBER")`，且 `createInvite` 方法直接呼叫 `TeamService.createInvite(teamId)`，沒有檢查當前使用者是否為該團隊成員。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:78</code> 測試未驗證邀請連結的正確性</summary>

在「should create a team invite」測試中，僅檢查 `inviteLink` 包含 `token`，但未驗證 `token` 是否為實際的隨機 token（而非 identifier）。由於目前 `createInvite` 回傳的 `token` 是 identifier，此測試仍會通過，無法捕捉到該 bug。建議增加對 token 格式的驗證，例如檢查其長度或與資料庫中的 token 比對。

**判斷依據**：測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token);` 僅檢查包含關係，未驗證 token 本身。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9193 (cache hit 9088) ｜ completion tokens 1286 ｜ PR #6</sub>