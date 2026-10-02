<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了團隊邀請連結的 API 端點（POST /v2/teams/:teamId/invite），包含控制器、模組、輸出 DTO 與 E2E 測試。主要風險在於權限控制：控制器使用 @Roles("TEAM_MEMBER")，但測試預期非管理員成員應被拒絕（403），這可能導致權限檢查不足，讓一般成員也能建立邀請連結。此外，TeamService.createInvite 的回傳值有變更，需確認其他呼叫端是否相容。建議優先修正權限角色定義，並確認 token 回傳值的正確性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 權限角色設定錯誤：@Roles("TEAM_MEMBER") 允許一般成員建立邀請連結 | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:99` | createInvite 回傳 token 改為 newToken.identifier，可能破壞既有呼叫端 | 0.80 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉，可能產生錯誤的邀請連結 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:19` | 測試使用 Jest 語法，可能違反專案規範 R08 | 0.60 |
| 🔸 | Minor | `packages/features/ee/teams/services/teamService.ts:567` | 檔案結尾缺少換行符號 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 權限角色設定錯誤：@Roles("TEAM_MEMBER") 允許一般成員建立邀請連結</summary>

控制器使用 @Roles("TEAM_MEMBER")，但 E2E 測試明確預期非管理員成員應收到 403。這表示一般成員也能呼叫此端點，違反了測試中的權限要求。應改為 @Roles("TEAM_ADMIN") 或相應的管理員角色。

失敗情境：任何具有 TEAM_MEMBER 角色的使用者都能為團隊建立邀請連結，導致未經授權的邀請發放。

**判斷依據**：diff 中新增的控制器第 28 行使用 @Roles("TEAM_MEMBER")，而測試檔案 teams-invite.controller.e2e-spec.ts 中「User is Team Member (not Admin)」區塊預期 403。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> createInvite 回傳 token 改為 newToken.identifier，可能破壞既有呼叫端</summary>

原本回傳的 token 是隨機產生的 token 字串，現在改為 newToken.identifier（即 `invite-link-for-teamId-${teamId}`）。這可能導致其他依賴此方法的程式碼（例如邀請連結驗證邏輯）無法正確運作，因為 identifier 並非實際的 token。

失敗情境：如果有其他程式碼使用 createInvite 的回傳 token 來驗證邀請，將無法匹配資料庫中的 token 欄位。

**判斷依據**：diff 中將原本的 `token` 改為 `newToken.identifier`，而 `newToken` 是 `prisma.verificationToken.create` 的結果，其 identifier 欄位是 `invite-link-for-teamId-${teamId}`，並非隨機 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉，可能產生錯誤的邀請連結</summary>

原本的條件是 `if (!isOrgContext)` 才回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這可能導致在非組織情境下，邀請連結會包含額外的 getting started 路徑，而組織情境下反而沒有。需要確認此變更是否符合預期。

失敗情境：非組織團隊的邀請連結可能錯誤地導向 getting started 頁面，或組織團隊的邀請連結缺少必要的 onboarding 路徑。

**判斷依據**：diff 中將 `if (!isOrgContext)` 改為 `if (isOrgContext)`，但未提供任何說明或測試來驗證此行為變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:19</code> 測試使用 Jest 語法，可能違反專案規範 R08</summary>

專案規範 R08 要求所有測試使用 Vitest 框架，但此測試檔案使用了 Jest 風格的 `describe`、`it`、`beforeAll`、`afterAll` 等全域函式，且未見 Vitest 的 import。若專案已全面遷移至 Vitest，此測試可能無法正確執行。

**判斷依據**：測試檔案開頭使用 `describe`，且未 import 任何測試框架，與 Vitest 的典型用法（`import { describe, it, expect } from 'vitest'`）不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/ee/teams/services/teamService.ts:567</code> 檔案結尾缺少換行符號</summary>

檔案最後一行 `}` 之後沒有換行符號，可能違反專案的格式化規範（R03）。建議在檔案結尾加上換行。

**判斷依據**：diff 顯示最後一行 `}` 沒有換行符號（`\ No newline at end of file`）。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7126 (cache hit 5632) ｜ completion tokens 1347 ｜ PR #6</sub>