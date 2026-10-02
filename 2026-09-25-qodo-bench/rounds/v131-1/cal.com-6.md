<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了團隊邀請連結的 API 端點，並包含對應的 e2e 測試。主要風險在於 `TeamService.createInvite` 的變更：回傳的 token 從原本的隨機 token 改為 `verificationToken.identifier`，且 `buildInviteLink` 的條件判斷被反轉，可能導致邀請連結的 token 與實際儲存的 token 不一致，或連結格式錯誤。此外，控制器使用 `@Roles("TEAM_MEMBER")` 但測試期望非管理員成員應被拒絕，這可能表示角色檢查邏輯有誤或測試情境不完整。建議優先修正 token 回傳與連結建構的邏輯，並釐清角色權限的預期行為。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:99` | 回傳的 token 與實際儲存的 token 不一致 | 0.95 |
| 🛑 | Blocker | `packages/features/ee/teams/services/teamService.ts:106` | buildInviteLink 條件判斷反轉，導致連結格式錯誤 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32` | 角色裝飾器可能允許非管理員成員建立邀請 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:209` | 測試清理可能不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:99</code> 回傳的 token 與實際儲存的 token 不一致</summary>

在 `createInvite` 中，原本回傳的是隨機產生的 `token`，但現在改為回傳 `newToken.identifier`。`identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位不是真正的邀請 token，而 `inviteLink` 中使用的 token 仍是原始的隨機 token，造成兩者不一致。使用者若使用回傳的 `token` 進行驗證，將無法成功加入團隊。

**建議**：回傳原始的 `token` 變數，而不是 `newToken.identifier`。

**判斷依據**：diff 中 `token: newToken.identifier,` 取代了原本的 `token,`，而 `newToken` 是 `prisma.verificationToken.create` 的結果，其 `identifier` 欄位是 `invite-link-for-teamId-${teamId}`，不是隨機 token。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/ee/teams/services/teamService.ts:106</code> buildInviteLink 條件判斷反轉，導致連結格式錯誤</summary>

原本的邏輯是：如果不是組織情境（`!isOrgContext`），直接回傳 `teamInviteLink`；否則（組織情境）會加上 getting started 路徑。修改後變成：如果是組織情境（`isOrgContext`），直接回傳 `teamInviteLink`；否則（非組織情境）才加上 getting started 路徑。這與原本的意圖相反，可能導致非組織團隊的邀請連結錯誤地包含 getting started 路徑，而組織團隊的連結缺少該路徑。

**建議**：將條件改回 `if (!isOrgContext)`，或確認變數名稱與邏輯是否正確。

**判斷依據**：diff 中 `if (!isOrgContext)` 被改為 `if (isOrgContext)`，但後續的程式碼區塊（取得 getting started 路徑）原本是在 `!isOrgContext` 為 false（即組織情境）時執行，現在邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32</code> 角色裝飾器可能允許非管理員成員建立邀請</summary>

控制器使用 `@Roles("TEAM_MEMBER")`，這表示任何團隊成員（包括一般成員）都可以呼叫此端點。然而，e2e 測試中有一個情境是「User is Team Member (not Admin)」預期會回傳 403。這可能表示角色檢查的邏輯有誤，或者測試情境與實際權限設計不一致。如果預期只有管理員可以建立邀請，應該使用 `@Roles("TEAM_ADMIN")` 或類似角色。

**建議**：確認此端點的權限需求，並調整 `@Roles` 裝飾器或測試期望。

**判斷依據**：控制器第 30 行使用 `@Roles("TEAM_MEMBER")`，但測試檔案中 `should fail to create invite as non-admin member` 預期 403，暗示一般成員不應有權限。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:209</code> 測試清理可能不完整</summary>

在 `afterAll` 中，測試刪除了使用者和團隊，但沒有刪除建立的 membership 記錄。這可能導致資料庫中殘留孤立的 membership 記錄，影響後續測試或資料一致性。

**建議**：在刪除團隊和使用者之前，先刪除相關的 membership，或使用 fixture 提供的刪除方法。

**判斷依據**：測試中建立了 membership，但在清理時未見刪除 membership 的程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5682 (cache hit 1408) ｜ completion tokens 1324 ｜ PR #6</sub>