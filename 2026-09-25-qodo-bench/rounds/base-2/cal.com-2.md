<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯抽成 MembershipRepository.hasPendingInviteByUserId，並在 onboarding getting-started 頁面新增伺服器端 redirect。主要風險在於新方法中 accepted 條件寫反（應為 false 卻寫成 true），導致行為與預期完全相反；此外測試資料清理不完整、測試依賴既有資料、以及 redirect 邏輯可能造成非預期跳轉。建議先修正 accepted 條件再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 的 accepted 條件寫反 | 0.99 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:27` | 測試資料清理不完整，可能污染其他測試 | 0.80 |
| ⚠️ | Major | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30` | redirect 條件可能過於寬鬆，導致非預期跳轉 | 0.75 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試依賴既有資料，可能不穩定 | 0.70 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | 條件由 AND 改為 OR，可能改變既有行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 的 accepted 條件寫反</summary>

方法名稱為 hasPendingInviteByUserId，但查詢條件為 `accepted: true`，這會回傳「已接受邀請」的 membership，而非 pending（未接受）。這導致呼叫端判斷完全相反：有 pending invite 的使用者不會被 redirect，沒有 pending invite 的使用者反而會被 redirect。

失敗情境：使用者註冊後有 pending team invite，呼叫此方法會回傳 false，因此不會 redirect 到 personal onboarding，與 PR 目的相反。

建議修正：將 `accepted: true` 改為 `accepted: false`。

**判斷依據**：diff 中新增的靜態方法內 `where` 條件為 `accepted: true`，而方法名稱與呼叫端邏輯都預期是 pending（未接受）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:27</code> 測試資料清理不完整，可能污染其他測試</summary>

在 `beforeAll` 中，如果找不到既有 team，會建立一個新 team 並記錄在 `createdTeamId`，但 `afterAll` 只刪除 `createdTeamId` 的 team，沒有刪除建立的 user。此外，測試中建立的 user 在部分測試中沒有被刪除（例如第一個測試在刪除 membership 後有刪除 user，但其他測試也有類似情況）。如果測試失敗或中斷，這些資料會殘留在資料庫中，影響後續測試或開發環境。

建議：使用 `try/finally` 確保每個測試建立的 user 和 membership 都被刪除，或使用測試資料庫交易回滾。

**判斷依據**：diff 中新增的測試檔案，`beforeAll` 建立 team 但 `afterAll` 只刪除 team，未刪除 user；且測試中建立的 user 刪除邏輯不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30</code> redirect 條件可能過於寬鬆，導致非預期跳轉</summary>

新增的 redirect 條件為 `if (hasPendingInvite)`，但 `hasPendingInviteByUserId` 目前因 accepted 條件錯誤而回傳「有已接受邀請」的使用者。即使修正為 accepted: false，此條件仍會將所有有 pending invite 的使用者直接導向 personal onboarding，可能跳過原本 getting-started 頁面應提供的其他資訊或步驟。需要確認產品邏輯是否預期如此。

建議：確認 redirect 的觸發條件是否應包含其他限制（例如 onboardingV3 flag），或與 `checkOnboardingRedirect` 的邏輯保持一致。

**判斷依據**：diff 中新增的 redirect 邏輯，直接根據 hasPendingInvite 決定跳轉，未考慮其他條件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試依賴既有資料，可能不穩定</summary>

在「should return true when user has both accepted and pending invites」測試中，使用 `prisma.team.findFirst` 尋找另一個 team（`id: { not: testTeamId }`），如果資料庫中沒有其他 team，則 `team2` 為 null，測試會跳過 pending membership 的建立，導致斷言變成 `expect(result).toBe(false)`，但測試名稱暗示應該回傳 true。這使得測試結果依賴環境，可能誤導。

建議：在測試中明確建立第二個 team，或使用 mock 資料。

**判斷依據**：diff 中測試檔案的第 87 行附近，尋找既有 team 作為第二個 team，若不存在則測試行為改變。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> 條件由 AND 改為 OR，可能改變既有行為</summary>

原本的條件是 `pendingInvite && onboardingV3Enabled`，現在改為 `hasPendingInvite || onboardingV3Enabled`。這表示只要 onboardingV3Enabled 為 true，即使沒有 pending invite，也會 redirect 到 personal onboarding。這可能不是預期行為，因為原本需要兩者同時成立。

失敗情境：使用者沒有 pending invite，但 onboardingV3 flag 開啟，現在會被強制導向 personal onboarding，可能跳過其他 onboarding 流程。

建議：確認是否應維持 AND 條件，或明確說明為何改為 OR。

**判斷依據**：diff 中將 `pendingInvite && onboardingV3Enabled` 改為 `hasPendingInvite || onboardingV3Enabled`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4607 (cache hit 4480) ｜ completion tokens 1616 ｜ PR #2</sub>