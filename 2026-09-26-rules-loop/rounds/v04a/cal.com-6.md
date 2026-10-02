<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了團隊邀請連結的 API v2 端點，包含控制器、輸出 DTO、模組與 e2e 測試。主要風險在於 `TeamService.createInvite` 的回傳值被改成 `newToken.identifier`，這會讓 API 回傳的 token 變成固定字串 `invite-link-for-teamId-{teamId}`，而不是實際的邀請 token，導致邀請連結失效。此外，`buildInviteLink` 的條件判斷被反轉，可能造成非組織團隊的邀請連結錯誤地導向 getting-started 流程。建議優先修正這兩個正確性問題，並補上對應的單元測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 是 identifier 而非實際 token，導致邀請連結失效 | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉，可能導致錯誤的邀請連結 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 權限檢查不足：僅使用 @Roles('TEAM_MEMBER')，未驗證使用者是否為該團隊成員 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:209` | 測試清理可能不完整：未刪除 memberships 資料 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 是 identifier 而非實際 token，導致邀請連結失效</summary>

在 `createInvite` 中，原本回傳的是 `token`（隨機產生的邀請 token），但現在改成 `newToken.identifier`。`identifier` 的值是 `invite-link-for-teamId-${teamId}`，這是一個固定字串，不是實際的邀請 token。這會導致 API 回傳的 `token` 欄位不正確，且 `inviteLink` 中的 token 也與資料庫中的 token 不符，使用者點擊邀請連結後將無法通過驗證。

**失敗情境**：任何呼叫此 API 的客戶端都會收到錯誤的 token，邀請連結無法使用。

**建議修法**：改回回傳 `token`，或如果確實需要回傳 identifier，則應同時回傳 token 並修正 `inviteLink` 的建構方式。

**判斷依據**：diff 中 `- token,` 改為 `+ token: newToken.identifier,`，而 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位在建立時被設定為 `invite-link-for-teamId-${teamId}`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉，可能導致錯誤的邀請連結</summary>

原本的邏輯是 `if (!isOrgContext)` 才回傳 `teamInviteLink`，否則回傳 getting-started 連結。現在改成 `if (isOrgContext)` 回傳 `teamInviteLink`，這會讓非組織團隊（`isOrgContext` 為 false）的邀請連結變成 getting-started 連結，而組織團隊反而拿到一般的團隊邀請連結。這與預期行為相反。

**失敗情境**：非組織團隊的邀請連結會錯誤地導向 getting-started 頁面，可能造成使用者混淆或流程錯誤。

**建議修法**：確認 `isOrgContext` 的語意，並修正條件判斷。

**判斷依據**：diff 中 `- if (!isOrgContext) {` 改為 `+ if (isOrgContext) {`，但後續的 `return teamInviteLink;` 與 getting-started 邏輯未變。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 權限檢查不足：僅使用 @Roles('TEAM_MEMBER')，未驗證使用者是否為該團隊成員</summary>

控制器使用 `@Roles('TEAM_MEMBER')` 來限制只有團隊成員可以建立邀請，但這個角色檢查可能只是檢查使用者的全域角色，而不是針對特定團隊的成員資格。攻擊者若擁有 `TEAM_MEMBER` 角色（例如在其他團隊中），可能可以為任意團隊建立邀請連結。

**失敗情境**：使用者 A 是團隊 X 的成員，但不是團隊 Y 的成員，但若 A 具有 `TEAM_MEMBER` 角色，則可以呼叫 `POST /v2/teams/Y/invite` 並成功建立邀請。

**建議修法**：在服務層或控制器中加入團隊成員資格的檢查，例如使用 `MembershipsService` 驗證使用者是否屬於該團隊。

**判斷依據**：控制器僅有 `@Roles('TEAM_MEMBER')`，且 `createInvite` 方法只接收 `teamId`，沒有進行團隊成員資格的驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:209</code> 測試清理可能不完整：未刪除 memberships 資料</summary>

在 `afterAll` 中，測試刪除了使用者和團隊，但沒有刪除建立的 membership 記錄。這可能導致資料庫中殘留孤立的 membership 資料，影響後續測試或資料一致性。

**建議修法**：在 `afterAll` 中一併刪除 membership，或使用 fixture 提供的刪除方法。

**判斷依據**：測試中建立了 membership，但在清理時未見刪除 membership 的程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6342 (cache hit 5632) ｜ completion tokens 1384 ｜ PR #6</sub>