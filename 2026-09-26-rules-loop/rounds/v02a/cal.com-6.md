<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了團隊邀請連結的 API endpoint，並修改了 TeamService.createInvite 的實作。主要風險在於 createInvite 回傳的 token 改為 verificationToken 的 identifier，但 identifier 是固定格式 `invite-link-for-teamId-${teamId}`，並非隨機 token，這會讓邀請連結失去唯一性與安全性。此外，buildInviteLink 的條件判斷被反轉，可能導致非組織情境下產生錯誤的連結。建議優先修正 token 的產生與回傳邏輯，並確認 buildInviteLink 的條件。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 不是隨機 token，而是固定的 identifier | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 的條件判斷被反轉，可能產生錯誤的邀請連結 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少權限檢查：任何 TEAM_MEMBER 都能為任意 teamId 建立邀請 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:36` | 缺少輸入驗證：teamId 僅用 ParseIntPipe，未驗證是否存在或是否為數字 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:10` | 測試檔案使用相對路徑 import，可能違反專案慣例 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 不是隨機 token，而是固定的 identifier</summary>

在 `createInvite` 中，原本回傳的是 `token`（隨機產生的 64 字元 hex），但修改後回傳 `newToken.identifier`。`identifier` 的值是 `invite-link-for-teamId-${teamId}`，這是一個可預測的字串，不具備 token 的隨機性。這會導致邀請連結中的 token 部分變成固定值，攻擊者只要知道 teamId 就能自行構造邀請連結，繞過邀請機制。

建議：回傳原本的 `token`（隨機值），而不是 `identifier`。

**判斷依據**：diff 中 `-    await prisma.verificationToken.create({` 改為 `+    const newToken = await prisma.verificationToken.create({`，且回傳值從 `-      token,` 改為 `+      token: newToken.identifier,`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 的條件判斷被反轉，可能產生錯誤的邀請連結</summary>

原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，表示非組織情境下直接回傳 teamInviteLink。修改後變成 `if (isOrgContext) { return teamInviteLink; }`，這會讓組織情境下回傳 teamInviteLink，而非組織情境下反而繼續執行後面的 getting started 路徑。這與函式名稱和預期行為不符，可能導致邀請連結錯誤。

建議：確認此條件是否應為 `if (!isOrgContext)`，或根據實際需求調整。

**判斷依據**：diff 中 `-    if (!isOrgContext) {` 改為 `+    if (isOrgContext) {`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少權限檢查：任何 TEAM_MEMBER 都能為任意 teamId 建立邀請</summary>

Controller 使用 `@Roles("TEAM_MEMBER")`，但沒有驗證目前使用者是否為該 team 的成員。這表示任何具有 TEAM_MEMBER 角色的使用者（可能是其他團隊的成員）都可以對任意 teamId 呼叫此 endpoint 並取得邀請連結。雖然 e2e 測試中非成員會得到 403，但那是因為 RolesGuard 只檢查角色，沒有檢查團隊成員資格。實際上，授權邏輯可能依賴於 TeamService.createInvite 內部的檢查，但從 diff 看不出來有這樣的檢查。

建議：在 controller 或 service 中加入團隊成員資格的驗證，確保只有該團隊的成員（且為 admin？）才能建立邀請。

**判斷依據**：diff 中新增的 controller 只有 `@Roles("TEAM_MEMBER")`，沒有其他團隊成員檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:36</code> 缺少輸入驗證：teamId 僅用 ParseIntPipe，未驗證是否存在或是否為數字</summary>

`@Param("teamId", ParseIntPipe)` 只確保 teamId 是整數，但沒有驗證該 team 是否存在。如果 teamId 不存在，TeamService.createInvite 可能會拋出錯誤，但錯誤處理可能不夠明確。建議加入 team 存在性的檢查，或使用全域 exception filter 處理。

**判斷依據**：diff 中 controller 的參數裝飾器。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:10</code> 測試檔案使用相對路徑 import，可能違反專案慣例</summary>

測試檔案中使用了 `test/fixtures/...` 和 `test/utils/...` 的相對路徑，但專案其他檔案可能使用 alias（如 `@/...`）。這可能違反專案的 import 慣例，但影響不大。

**判斷依據**：diff 中新增的測試檔案 import 語句。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7157 (cache hit 1536) ｜ completion tokens 1426 ｜ PR #6</sub>