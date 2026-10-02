<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了在 onboarding 頁面檢查 pending team invites 並重新導向的邏輯，並將查詢封裝到 MembershipRepository。主要風險在於 `hasPendingInviteByUserId` 的實作查詢條件錯誤（`accepted: true` 而非 `false`），導致功能完全失效；此外，`checkOnboardingRedirect` 中的條件變更可能改變既有行為。測試檔案存在資料清理與相依性問題。建議先修正查詢條件並補齊測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:584` | hasPendingInviteByUserId 查詢條件錯誤，永遠回傳 false | 0.99 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | checkOnboardingRedirect 條件變更可能導致錯誤重新導向 | 0.85 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:39` | 測試資料清理不完整，可能影響其他測試 | 0.80 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試依賴資料庫中已存在的 team，可能不穩定 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:584</code> hasPendingInviteByUserId 查詢條件錯誤，永遠回傳 false</summary>

此方法用於檢查使用者是否有 pending invite，但查詢條件為 `accepted: true`，這會找出已接受的 membership，而非未接受的邀請。因此，當使用者有 pending invite 時，此方法會回傳 `false`，導致 PR 的主要功能（重新導向）完全失效。

**失敗情境**：使用者透過邀請連結註冊，系統建立了 `accepted: false` 的 membership。當使用者進入 `/onboarding/getting-started` 頁面時，`hasPendingInviteByUserId` 回傳 `false`，因此不會重新導向到 `/onboarding/personal/settings`，使用者會停留在錯誤的頁面。

**建議修法**：將查詢條件改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法，其 `where` 條件為 `accepted: true`，但方法名稱與用途皆指向 pending invite（未接受）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> checkOnboardingRedirect 條件變更可能導致錯誤重新導向</summary>

原本的邏輯是：只有當 `pendingInvite` 存在且 `onboardingV3Enabled` 為 true 時，才重新導向到 `/onboarding/personal/settings`。修改後變成 `if (hasPendingInvite || onboardingV3Enabled)`，這表示只要 `onboardingV3Enabled` 為 true，無論是否有 pending invite，都會重新導向到 `/onboarding/personal/settings`。這可能導致沒有 pending invite 的使用者也被重新導向，跳過原本的 onboarding 流程。

**失敗情境**：假設 `onboardingV3Enabled` 為 true，且使用者沒有 pending invite。原本應進入 `/onboarding/getting-started`，但修改後會直接進入 `/onboarding/personal/settings`，可能跳過必要的步驟。

**建議修法**：確認此變更是否為預期行為。若否，應改回 `if (hasPendingInvite && onboardingV3Enabled)`。

**判斷依據**：diff 中將原本的 `if (pendingInvite && onboardingV3Enabled)` 改為 `if (hasPendingInvite || onboardingV3Enabled)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:39</code> 測試資料清理不完整，可能影響其他測試</summary>

在 `beforeAll` 中，如果找不到現有 team，會建立一個新 team 並記錄其 ID 到 `createdTeamId`，但在 `afterAll` 中刪除該 team 時，並未先刪除與之相關的 memberships。這可能導致外鍵約束錯誤，或殘留測試資料。此外，測試中建立的 user 在部分測試中未於 `afterEach` 清理，可能造成資料累積。

**失敗情境**：若 `afterAll` 執行時仍有 membership 參照該 team，刪除 team 會因外鍵約束失敗，導致測試套件報錯。

**建議修法**：在 `afterAll` 中先刪除所有與該 team 相關的 memberships，再刪除 team；或使用資料庫交易或測試框架的清理機制。

**判斷依據**：diff 中新增的測試檔案，`afterAll` 直接刪除 team，未處理關聯的 memberships。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試依賴資料庫中已存在的 team，可能不穩定</summary>

在測試 `should return true when user has both accepted and pending invites` 中，使用 `prisma.team.findFirst` 尋找另一個 team（`id: { not: testTeamId }`）。如果資料庫中沒有其他 team，則 `team2` 為 null，測試會降級為只驗證 accepted membership 的情況，無法完整測試混合情境。這使得測試結果取決於資料庫狀態，可能不穩定。

**建議修法**：在測試中建立所需的第二個 team，或使用 mock 資料。

**判斷依據**：diff 中測試檔案第 128 行附近，依賴資料庫中已存在的 team。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7613 (cache hit 1536) ｜ completion tokens 1507 ｜ PR #2</sub>