<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，包含控制器、輸出 DTO、模組與測試。主要風險在於 `TeamService.createInvite` 的變更：回傳值從 token 改為 identifier，但 identifier 是固定字串，可能導致每次呼叫回傳相同 token，且 `buildInviteLink` 的條件判斷被反轉，可能產生錯誤的邀請連結。此外，控制器使用 `@Roles("TEAM_MEMBER")` 但測試預期非管理員成員應被拒絕，權限邏輯可能不一致。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳值錯誤：應回傳 token 而非 identifier | 0.95 |
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:106` | 條件判斷反轉：isOrgContext 的邏輯錯誤 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 權限裝飾器與測試預期不符 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:35` | 缺少請求主體驗證 | 0.60 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:19` | 測試使用 Jest 而非 Vitest | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳值錯誤：應回傳 token 而非 identifier</summary>

在 `createInvite` 方法中，原本回傳 `token`，但修改後回傳 `newToken.identifier`。`identifier` 是固定字串 `invite-link-for-teamId-${teamId}`，並非隨機產生的 token。這會導致每次呼叫都回傳相同的值，且該值並非實際的邀請 token，使得邀請連結失效。

**失敗情境**：呼叫 `POST /v2/teams/:teamId/invite` 後，回應中的 `token` 欄位會是 `invite-link-for-teamId-123`，而非隨機 token。使用此 token 建構的邀請連結將無法驗證。

**建議**：改回傳 `token` 變數，或若需要 identifier，應同時回傳兩者。

**判斷依據**：diff 中 `-      token,` 改為 `+      token: newToken.identifier,`，而 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位在建立時設定為固定字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> 條件判斷反轉：isOrgContext 的邏輯錯誤</summary>

在 `buildInviteLink` 方法中，原本 `if (!isOrgContext)` 改為 `if (isOrgContext)`，導致非組織情境下會執行組織專屬的邏輯（取得 getting started 路徑），而組織情境下反而回傳基本連結。這會產生錯誤的邀請連結。

**失敗情境**：當團隊不是組織或不在組織中時（`isOrgContext` 為 false），原本應回傳基本連結，但現在會嘗試取得 getting started 路徑，可能導致錯誤或非預期的行為。反之，組織情境下會回傳基本連結，缺少必要的 onboarding 路徑。

**建議**：改回 `if (!isOrgContext)`。

**判斷依據**：diff 中 `-    if (!isOrgContext) {` 改為 `+    if (isOrgContext) {`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 權限裝飾器與測試預期不符</summary>

控制器使用 `@Roles("TEAM_MEMBER")`，但測試中預期非管理員成員（MEMBER）應回傳 403。這表示權限邏輯可能不正確：若 `TEAM_MEMBER` 角色允許所有成員，則測試會失敗；若 `TEAM_MEMBER` 僅允許管理員，則角色名稱具有誤導性。

**失敗情境**：以一般成員身分呼叫端點，預期應被拒絕（403），但若 `TEAM_MEMBER` 角色包含一般成員，則請求會成功，導致測試失敗。

**建議**：確認角色定義，若僅管理員可建立邀請，應使用 `TEAM_ADMIN` 或類似角色。

**判斷依據**：控制器中 `@Roles("TEAM_MEMBER")`，而測試 `should fail to create invite as non-admin member` 預期 403。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:35</code> 缺少請求主體驗證</summary>

端點不需要任何請求主體，但未使用 DTO 進行驗證。雖然目前沒有輸入，但未來擴充時可能遺漏驗證。此外，Swagger 文件中未定義回應結構，可能導致文件不完整。

**建議**：考慮使用 `@Body()` 搭配 DTO 進行驗證，並在 Swagger 中定義回應型別。

**判斷依據**：控制器方法僅有 `@Param`，沒有 `@Body` 或 `@Query` 驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:19</code> 測試使用 Jest 而非 Vitest</summary>

根據規範 R08，所有測試必須使用 Vitest 框架。此測試檔案使用 `describe`、`it`、`expect` 等 Jest 風格 API，但未使用 Vitest 特有的 `vi` 物件。若專案已全面遷移至 Vitest，此測試可能無法執行。

**建議**：確認測試框架，若為 Vitest，應改用 `vi.fn()` 等 API，或調整配置。

**判斷依據**：測試檔案使用 Jest 風格的 `describe` 和 `it`，未見 Vitest 的 `vi` 導入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7157 (cache hit 7040) ｜ completion tokens 1554 ｜ PR #6</sub>