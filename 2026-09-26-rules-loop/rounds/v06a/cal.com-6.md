<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，包含控制器、模組、輸出 DTO 與 E2E 測試。主要風險在於 `TeamService.createInvite` 的回傳值變更：原本回傳 token，現在改回傳 `newToken.identifier`（即 `invite-link-for-teamId-${teamId}`），這會導致回傳的 token 不再是實際的邀請 token，而是 identifier，可能造成邀請連結失效或安全性問題。此外，`buildInviteLink` 的條件判斷邏輯被反轉，可能影響非組織情境下的連結生成。建議優先修正這兩個問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 是 identifier 而非實際 token | 0.95 |
| ⚠️ | Major | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷邏輯反轉 | 0.85 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 權限檢查可能不足：僅使用 @Roles("TEAM_MEMBER") | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1` | 測試使用 Jest 而非 Vitest，違反 R08 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1` | 測試未設定 UTC 時區，可能違反 R08 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 是 identifier 而非實際 token</summary>

在 `createInvite` 中，原本回傳 `token`（隨機生成的 64 字元 hex），現在改為回傳 `newToken.identifier`（即 `invite-link-for-teamId-${teamId}`）。這會導致 API 回傳的 `token` 欄位不再是實際的邀請 token，而是 identifier。任何使用此 token 進行驗證或加入團隊的流程都會失敗，因為資料庫中儲存的 token 是隨機值，而 identifier 只是用於查詢的鍵。

**失敗情境**：使用者取得邀請連結後，點擊連結並使用回傳的 token 進行驗證，但系統會以 identifier 作為 token 查詢，找不到對應的 verificationToken，導致邀請無效。

**建議**：回傳原本的 `token` 變數，而不是 `newToken.identifier`。

**判斷依據**：diff 中 `-      token,` 改為 `+      token: newToken.identifier,`，且 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位是 `invite-link-for-teamId-${teamId}`，並非隨機 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷邏輯反轉</summary>

原本的條件是 `if (!isOrgContext)`，代表非組織情境時直接回傳 `teamInviteLink`；現在改為 `if (isOrgContext)`，代表組織情境時直接回傳 `teamInviteLink`，非組織情境則會進入後續的 `OnboardingPathService.getGettingStartedPathWhenInvited` 邏輯。這與函式名稱和預期行為相反，可能導致非組織團隊的邀請連結被錯誤地加上 onboarding 路徑，或組織團隊的邀請連結缺少必要的 onboarding 路徑。

**失敗情境**：當 `isOrgContext` 為 `false`（非組織團隊）時，原本應直接回傳 `teamInviteLink`，但現在會執行 `getGettingStartedPathWhenInvited`，可能產生錯誤的連結或額外的副作用。

**建議**：確認此邏輯變更是否為預期行為；若不是，請改回 `if (!isOrgContext)`。

**判斷依據**：diff 中 `-    if (!isOrgContext) {` 改為 `+    if (isOrgContext) {`，且後續程式碼未變更，顯示條件判斷被反轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 權限檢查可能不足：僅使用 @Roles("TEAM_MEMBER")</summary>

控制器使用 `@Roles("TEAM_MEMBER")` 來限制只有團隊成員可以建立邀請，但未檢查使用者是否為團隊管理員。根據測試，非管理員成員應該無法建立邀請（預期 403），但目前的角色設定可能允許任何團隊成員（包括 MEMBER）呼叫此端點。需要確認 `RolesGuard` 的實作是否會進一步檢查團隊內的角色，否則這將是一個權限提升漏洞。

**失敗情境**：一個普通團隊成員（MEMBER）呼叫此端點，若 `RolesGuard` 僅檢查全域角色而非團隊內角色，則可能成功建立邀請，違反預期的權限控制。

**建議**：確認 `RolesGuard` 是否有團隊層級的角色檢查；若無，應加入額外的 guard 或服務層檢查，確保只有 ADMIN 可以建立邀請。

**判斷依據**：控制器使用 `@Roles("TEAM_MEMBER")`，但測試中非管理員成員預期 403，暗示需要更嚴格的權限檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1</code> 測試使用 Jest 而非 Vitest，違反 R08</summary>

此測試檔案使用 Jest 風格的 `describe`、`it`、`beforeAll` 等，但根據規範 R08，所有測試必須使用 Vitest 框架。雖然語法相似，但若專案已全面遷移至 Vitest，此測試可能無法被正確執行或收集。

**建議**：確認專案測試框架；若為 Vitest，請改用 `import { describe, it, beforeAll, afterAll, expect } from 'vitest'` 並調整相關設定。

**判斷依據**：檔案中未見 Vitest 的 import，且使用 Jest 風格的測試語法，可能違反 R08。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:1</code> 測試未設定 UTC 時區，可能違反 R08</summary>

規範 R08 要求測試命令設定 `TZ=UTC`，但此測試檔案本身未設定時區，且未見相關配置。若測試涉及時間相關邏輯，可能在不同時區下失敗。

**建議**：確保測試執行環境設定 `TZ=UTC`，或在測試設定中全域設定。

**判斷依據**：測試檔案中未見時區設定，且規範 R08 要求 UTC。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7147 (cache hit 5632) ｜ completion tokens 1682 ｜ PR #6</sub>