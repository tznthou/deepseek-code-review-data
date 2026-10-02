<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，包含控制器、輸出 DTO、模組與 e2e 測試。主要風險在於 `TeamService.createInvite` 的回傳值變更：原本回傳 `token`，現在改為回傳 `newToken.identifier`，但 `identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳錯誤的 token，且 `inviteLink` 仍使用正確的 token 建構，造成兩者不一致。此外，`buildInviteLink` 的條件判斷被反轉，可能影響邀請連結的格式。建議優先修正 token 回傳值，並確認條件反轉的意圖。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳錯誤的 token：應回傳 `token` 而非 `newToken.identifier` | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | `buildInviteLink` 條件判斷反轉，可能導致錯誤的邀請連結格式 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:35` | 缺少對 `teamId` 的權限驗證，任何團隊成員都可能為任意團隊建立邀請 | 0.75 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1` | 測試檔案使用 Jest 語法，違反專案規範 R08（應使用 Vitest） | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳錯誤的 token：應回傳 `token` 而非 `newToken.identifier`</summary>

在 `createInvite` 方法中，原本回傳 `token`（隨機產生的邀請 token），但修改後回傳 `newToken.identifier`。`identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位錯誤，而 `inviteLink` 仍使用正確的 token 建構，造成兩者不一致。

**失敗情境**：當客戶端使用回傳的 `token` 來驗證邀請時，會因為 token 不正確而失敗。

**建議**：改回傳 `token`，或如果確實需要回傳 identifier，請同步更新 `inviteLink` 的建構方式，並確保兩者一致。

**判斷依據**：diff 中 `-    token,` 改為 `+    token: newToken.identifier,`，且 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位為 `invite-link-for-teamId-${teamId}`，並非隨機 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> `buildInviteLink` 條件判斷反轉，可能導致錯誤的邀請連結格式</summary>

原本的條件是 `if (!isOrgContext)`，現在改為 `if (isOrgContext)`。這會反轉行為：當 `isOrgContext` 為 true 時，直接回傳 `teamInviteLink`；否則會執行後續的 `gettingStartedPath` 邏輯。需要確認此變更是否符合預期。

**失敗情境**：如果 `isOrgContext` 的語義是「是否為組織或組織中的團隊」，則反轉後可能導致非組織團隊的邀請連結被錯誤地加上 getting started 路徑，或組織團隊的邀請連結缺少該路徑。

**建議**：確認 `isOrgContext` 的定義，並驗證此條件反轉是否為有意為之。如果不是，請恢復原本的條件。

**判斷依據**：diff 中 `-    if (!isOrgContext) {` 改為 `+    if (isOrgContext) {`，條件反轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:35</code> 缺少對 `teamId` 的權限驗證，任何團隊成員都可能為任意團隊建立邀請</summary>

控制器使用 `@Roles("TEAM_MEMBER")` 來限制只有團隊成員可以存取，但沒有驗證目前使用者是否屬於 `:teamId` 指定的團隊。這表示任何具有 `TEAM_MEMBER` 角色的使用者（可能來自其他團隊）都可以為任意團隊建立邀請連結。

**失敗情境**：攻擊者取得任何團隊成員的 API 金鑰後，可以為任意團隊建立邀請連結，進而加入該團隊。

**建議**：在控制器或服務層加入團隊成員資格檢查，確保目前使用者是該團隊的成員（且可能需為管理員）。

**判斷依據**：控制器方法僅接收 `teamId` 參數，沒有使用 `@GetUser()` 取得目前使用者，也沒有呼叫任何成員資格驗證服務。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1</code> 測試檔案使用 Jest 語法，違反專案規範 R08（應使用 Vitest）</summary>

專案規範 R08 要求所有測試使用 Vitest 框架，但此測試檔案使用了 Jest 的 `describe`、`it`、`beforeAll`、`afterAll` 等全域函式，且沒有從 `vitest` 匯入。這可能導致測試在 Vitest 環境下無法正確執行。

**建議**：將測試改為使用 Vitest 的匯入方式，例如 `import { describe, it, beforeAll, afterAll } from "vitest"`，並確認測試命令設定 `TZ=UTC`。

**判斷依據**：測試檔案中使用了 Jest 風格的測試函式，且沒有匯入 Vitest 的相關 API。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7167 (cache hit 5632) ｜ completion tokens 1440 ｜ PR #6</sub>