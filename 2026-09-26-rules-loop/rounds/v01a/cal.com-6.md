<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點（POST /v2/teams/:teamId/invite），包含控制器、輸出 DTO、模組註冊與 E2E 測試。主要風險在於 TeamService.createInvite 的修改：原本回傳 token，現在改回傳 identifier，但 identifier 是固定字串，可能導致邀請連結失效或安全性問題。此外，buildInviteLink 的條件判斷被反轉，可能造成非組織團隊的邀請連結錯誤。測試涵蓋了管理員、非管理員成員與非成員的情境，但未驗證邀請連結的實際可用性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳 identifier 而非 token 導致邀請連結失效 | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 缺少 teamId 的權限驗證 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1` | 測試使用 Jest 而非 Vitest | 0.70 |
| 🔸 | Minor | `packages/features/ee/teams/services/teamService.ts:567` | 檔案結尾缺少換行符 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳 identifier 而非 token 導致邀請連結失效</summary>

在 createInvite 方法中，原本回傳 `token`（隨機產生的 64 字元 hex 字串），現在改為回傳 `newToken.identifier`。但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，這是一個固定且可預測的字串，並非隨機 token。這會導致：
1. 邀請連結中的 token 參數變成固定值，任何人都可以猜測並存取邀請連結，喪失安全性。
2. 前端或後續流程若依賴 token 的唯一性來驗證邀請，將無法正確運作。
建議改回回傳 `token`，或確認 `identifier` 的用途後修正。

**判斷依據**：diff 中原本的 `token,` 被改為 `token: newToken.identifier,`，而 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位在建立時被設定為 `invite-link-for-teamId-${teamId}`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉</summary>

原本的條件是 `if (!isOrgContext)`，現在改為 `if (isOrgContext)`。這會導致：
- 當 `isOrgContext` 為 true（組織或組織中的團隊）時，回傳的邀請連結是 `/teams?token=...`，但這可能不是預期的組織邀請連結格式。
- 當 `isOrgContext` 為 false（非組織團隊）時，會進入 `OnboardingPathService.getGettingStartedPathWhenInvited` 分支，產生帶有 callbackUrl 的連結，但這可能不適用於非組織團隊。
需要確認此條件反轉是否為預期行為，否則應修正。

**判斷依據**：diff 中 `if (!isOrgContext)` 被改為 `if (isOrgContext)`，且後續的 return 邏輯未變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 缺少 teamId 的權限驗證</summary>

控制器使用 `@Roles("TEAM_MEMBER")` 來限制只有團隊成員可以呼叫，但沒有驗證目前使用者是否屬於 `teamId` 指定的團隊。這可能導致任何已驗證的使用者（具有 TEAM_MEMBER 角色）可以為任意團隊建立邀請連結，只要他們知道 teamId。建議在服務層或控制器中加入團隊成員資格的檢查。

**判斷依據**：控制器中只有 `@Roles("TEAM_MEMBER")` 裝飾器，沒有使用 `@GetUser()` 取得使用者資訊，也沒有呼叫任何服務來驗證團隊成員資格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1</code> 測試使用 Jest 而非 Vitest</summary>

此測試檔案使用 `describe`、`it`、`beforeAll` 等 Jest 風格的 API，但專案規範 [R08] 要求所有測試使用 Vitest。雖然 Vitest 相容 Jest API，但若專案已全面遷移至 Vitest，此檔案可能不符合規範。建議確認測試框架並調整。

**判斷依據**：檔案中使用了 Jest 風格的 import 與測試結構，且未見 Vitest 特有的 import（如 `import { describe, it, expect } from 'vitest'`）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/ee/teams/services/teamService.ts:567</code> 檔案結尾缺少換行符</summary>

diff 顯示檔案結尾的 `}` 之後沒有換行符（`\ No newline at end of file`）。這可能違反專案的格式化規範 [R03]（使用 LF 行尾）。建議在檔案結尾加上換行符。

**判斷依據**：diff 中最後一行顯示 `-}` 和 `+}` 且標記 `\ No newline at end of file`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7157 (cache hit 5632) ｜ completion tokens 1400 ｜ PR #6</sub>