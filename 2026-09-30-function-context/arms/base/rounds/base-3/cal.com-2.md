<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 onboarding 頁面的 pending invite 檢查抽成 MembershipRepository 的靜態方法，並在 getting-started 頁面新增伺服器端 redirect。主要風險在於新方法 `hasPendingInviteByUserId` 的查詢條件寫成 `accepted: true`，與方法名稱及預期行為相反，會導致有 pending invite 的使用者不被重導向，而沒有 pending invite 的使用者反而被重導向。此外，整合測試的清理邏輯有缺陷，可能留下測試資料。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false | 0.99 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:61` | 測試清理邏輯不完整，可能殘留測試資料 | 0.90 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試依賴既有資料，可能不穩定 | 0.85 |
| ⚠️ | Major | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30` | 新增的 redirect 可能造成無限重導向迴圈 | 0.80 |
| 🔸 | Minor | `packages/features/auth/lib/onboardingUtils.ts:69` | 條件邏輯變更可能影響既有行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false</summary>

方法名稱為 `hasPendingInviteByUserId`，但查詢條件使用 `accepted: true`，這會導致：
- 有 pending invite（accepted: false）的使用者，此方法回傳 false，不會被重導向。
- 沒有 pending invite 但已有 accepted membership 的使用者，此方法回傳 true，被錯誤重導向。

這與 PR 目的完全相反。應將條件改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱與呼叫處都期望檢查 pending invite（即 accepted: false）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:61</code> 測試清理邏輯不完整，可能殘留測試資料</summary>

在 `should return true when user has a pending invite (accepted: false)` 測試中，手動刪除 membership 後將 `createdMembershipIds.length = 0`，但 `afterEach` 仍會執行 `clearTestMemberships`，此時陣列已空，不會重複刪除。然而，若測試中途失敗（例如 `expect` 失敗），`afterEach` 會執行 `clearTestMemberships`，但 `createdMembershipIds` 可能未包含該 membership（因為 push 在 create 之後，若 create 失敗則不會 push），導致資料殘留。建議使用 try/finally 或將清理邏輯統一在 `afterEach` 中，並確保所有建立的資料都被追蹤。

**判斷依據**：測試中手動刪除 membership 並清空陣列，但若測試失敗，`afterEach` 無法清理未追蹤的資料。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試依賴既有資料，可能不穩定</summary>

在 `should return true when user has both accepted and pending invites` 測試中，使用 `prisma.team.findFirst` 尋找另一個 team（`id: { not: testTeamId }`），若資料庫中沒有其他 team，則 `team2` 為 null，測試會降級為只驗證 accepted membership 的情況，無法真正測試混合情境。這使得測試結果依賴於測試環境的既有資料，可能導致測試不穩定或覆蓋率不足。建議在測試中建立第二個 team，或使用獨立的測試資料。

**判斷依據**：測試中尋找既有 team，若不存在則跳過 pending invite 的建立，導致測試情境不完整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30</code> 新增的 redirect 可能造成無限重導向迴圈</summary>

在 `getting-started` 頁面新增 redirect 到 `/onboarding/personal/settings`，但若該頁面也執行相同的 pending invite 檢查並 redirect 回來，可能形成迴圈。需要確認 `/onboarding/personal/settings` 的邏輯是否會再次觸發 redirect。

**判斷依據**：新增的 redirect 目標頁面可能也有類似的檢查，若未處理可能造成迴圈。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> 條件邏輯變更可能影響既有行為</summary>

原本條件為 `pendingInvite && onboardingV3Enabled`，現在改為 `hasPendingInvite || onboardingV3Enabled`。這表示即使沒有 pending invite，只要 `onboardingV3Enabled` 為 true，就會 redirect 到 `/onboarding/personal/settings`。這可能是預期行為，但需確認是否會影響其他流程。

**判斷依據**：diff 中條件從 `&&` 改為 `||`，可能改變 redirect 行為。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4607 (cache hit 4480) ｜ completion tokens 1452 ｜ PR #2</sub>