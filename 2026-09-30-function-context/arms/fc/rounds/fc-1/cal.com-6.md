<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，包含控制器、模組、輸出 DTO 與端對端測試，並修改了 TeamService.createInvite 的邏輯。主要風險在於 createInvite 中回傳的 token 改為 identifier，可能導致邀請連結失效；此外，buildInviteLink 的條件判斷被反轉，可能造成非組織團隊產生錯誤的邀請連結。建議優先修正這兩個邏輯錯誤，並補齊權限驗證與測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | createInvite 回傳錯誤的 token 欄位 | 0.95 |
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少團隊管理員權限驗證 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38` | 未處理團隊不存在或無權限的例外 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:73` | 測試未驗證邀請連結的實際可用性 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> createInvite 回傳錯誤的 token 欄位</summary>

在 `createInvite` 中，原本回傳 `token`（隨機產生的 token），但修改後回傳 `newToken.identifier`。`identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致回傳給客戶端的 token 不正確，邀請連結中的 token 也與資料庫中的 token 不一致，使用者將無法透過該 token 加入團隊。

建議改回傳 `token` 變數，或明確使用 `newToken.token`。

**判斷依據**：diff 中 `-    await prisma.verificationToken.create({` 改為 `+    const newToken = await prisma.verificationToken.create({`，且回傳值從 `-      token,` 改為 `+      token: newToken.identifier,`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉</summary>

原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，代表非組織情境使用團隊邀請連結；修改後變成 `if (isOrgContext) { return teamInviteLink; }`，導致組織情境反而回傳團隊邀請連結，非組織情境則回傳組織邀請連結。這會讓邀請連結的格式錯誤，使用者可能被導向錯誤的頁面。

建議將條件改回 `if (!isOrgContext)`，或根據實際需求調整。

**判斷依據**：diff 中 `-    if (!isOrgContext) {` 改為 `+    if (isOrgContext) {`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少團隊管理員權限驗證</summary>

控制器使用 `@Roles("TEAM_MEMBER")`，但建立邀請連結通常需要管理員權限。目前任何團隊成員（甚至非管理員）都可以呼叫此端點，可能導致權限提升。建議改為 `@Roles("TEAM_ADMIN")` 或加入自訂的權限檢查，確保只有管理員能建立邀請。

**判斷依據**：控制器中 `@Roles("TEAM_MEMBER")` 裝飾器，且測試中非管理員成員預期 403，但實際可能通過。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38</code> 未處理團隊不存在或無權限的例外</summary>

`TeamService.createInvite` 在團隊不存在時會拋出 `ErrorWithCode(ErrorCode.NotFound)`，但控制器未捕獲此例外，可能導致 500 錯誤而非 404。建議加入例外處理或使用全域例外過濾器，確保回傳適當的 HTTP 狀態碼。

**判斷依據**：控制器直接呼叫 `TeamService.createInvite`，未使用 try/catch 或檢查回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:73</code> 測試未驗證邀請連結的實際可用性</summary>

測試僅檢查 token 長度大於 0 且 inviteLink 包含 token，但未驗證該 token 是否真的存在於資料庫且未過期。建議加入後續使用該 token 加入團隊的測試，以確保邀請流程完整。

**判斷依據**：測試中僅有基本斷言，未涵蓋邀請連結的實際使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9193 (cache hit 1536) ｜ completion tokens 1323 ｜ PR #6</sub>