<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了團隊邀請連結的 API 端點，包含控制器、輸出 DTO、模組與 e2e 測試。主要風險在於 `TeamService.createInvite` 的回傳值被改為 `newToken.identifier`，這會讓 API 回傳的 token 變成 `invite-link-for-teamId-<id>` 而非實際的邀請 token，導致邀請連結失效。此外，`buildInviteLink` 的條件判斷被反轉，可能造成非組織團隊的邀請連結錯誤。測試方面，e2e 測試使用 Jest 語法，違反專案規範 R08。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 錯誤：使用 identifier 而非實際 token | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:19` | [R08] 測試使用 Jest 語法，違反專案規範 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少 teamId 的權限驗證 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:35` | 缺少輸入驗證 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 錯誤：使用 identifier 而非實際 token</summary>

在 `createInvite` 方法中，原本回傳的是 `token`（隨機產生的邀請 token），但修改後回傳 `newToken.identifier`。`identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位不正確，且 `inviteLink` 中的 token 也與回傳的 token 不一致，邀請連結將無法使用。

**失敗情境**：呼叫 `POST /v2/teams/:teamId/invite` 後，回應中的 `data.token` 會是 `invite-link-for-teamId-123`，而 `data.inviteLink` 中的 token 是隨機產生的 hex 字串。使用者若使用回應中的 token 或連結，將無法加入團隊。

**建議**：改回傳 `token`，而不是 `newToken.identifier`。

**判斷依據**：diff 中將原本的 `token,` 改為 `token: newToken.identifier,`，而 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位是 `invite-link-for-teamId-${teamId}`，不是隨機 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉</summary>

原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，表示非組織團隊直接回傳基本邀請連結。修改後變成 `if (isOrgContext) { return teamInviteLink; }`，這會導致組織團隊回傳基本連結，而非組織團隊卻進入後續的 getting started 路徑，行為完全相反。

**失敗情境**：當 `isOrgContext` 為 true（組織團隊）時，原本應該回傳包含 getting started 路徑的連結，但現在會直接回傳 `/teams?token=...`；反之，非組織團隊會錯誤地進入 getting started 流程。

**建議**：恢復原本的條件判斷，或確認此修改是否為預期行為。

**判斷依據**：diff 中將 `if (!isOrgContext)` 改為 `if (isOrgContext)`，且後續的 getting started 邏輯原本只在非組織團隊時執行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:19</code> [R08] 測試使用 Jest 語法，違反專案規範</summary>

專案規範 R08 要求所有測試使用 Vitest 框架，但此 e2e 測試檔案使用了 Jest 的 `describe`、`it`、`beforeAll`、`afterAll` 等全域函式，且未從 `@jest/globals` 或 Vitest 匯入。這會導致測試在 Vitest 環境下無法正確執行，或與專案其他測試不一致。

**建議**：改用 Vitest 的 `describe`、`it`、`beforeAll`、`afterAll`，並從 `vitest` 匯入。

**判斷依據**：檔案中使用了 Jest 風格的測試語法，且未見任何 Vitest 匯入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少 teamId 的權限驗證</summary>

控制器使用 `@Roles("TEAM_MEMBER")` 來限制只有團隊成員可以呼叫，但沒有驗證當前使用者是否屬於 `teamId` 指定的團隊。任何具有 `TEAM_MEMBER` 角色的使用者（可能是其他團隊的成員）都可以為任意團隊建立邀請連結。

**失敗情境**：使用者 A 是團隊 X 的成員，但可以呼叫 `POST /v2/teams/Y/invite` 為團隊 Y 建立邀請連結，只要 A 具有 `TEAM_MEMBER` 角色。

**建議**：在服務層或控制器中加入團隊成員資格檢查，確認當前使用者是該團隊的成員（且可能需要 ADMIN 角色）。

**判斷依據**：控制器僅使用 `@Roles("TEAM_MEMBER")`，沒有額外的團隊成員資格驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:35</code> 缺少輸入驗證</summary>

控制器方法沒有對 `teamId` 進行任何驗證，僅使用 `ParseIntPipe` 確保是整數。如果 `teamId` 不存在，`TeamService.createInvite` 可能會拋出未處理的錯誤，導致 500 回應。

**建議**：在服務層處理團隊不存在的情況，回傳適當的 404 錯誤。

**判斷依據**：控制器直接呼叫 `TeamService.createInvite(teamId)`，沒有檢查團隊是否存在。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7126 (cache hit 7040) ｜ completion tokens 1627 ｜ PR #6</sub>