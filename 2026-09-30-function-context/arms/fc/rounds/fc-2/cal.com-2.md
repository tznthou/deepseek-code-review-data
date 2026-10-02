<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了在 onboarding 頁面檢查 pending invite 並重導向的邏輯，並將查詢封裝至 MembershipRepository。主要風險在於 `hasPendingInviteByUserId` 的實作查詢條件為 `accepted: true`，與方法名稱及預期行為相反，可能導致重導向邏輯失效或錯誤重導向。此外，測試中對既有資料的依賴可能造成不穩定。建議優先修正查詢條件並強化測試隔離。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:584` | hasPendingInviteByUserId 查詢條件錯誤：使用 accepted: true 而非 false | 0.95 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:23` | 測試依賴既有資料，可能導致不穩定 | 0.80 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試案例「should return true when user has both accepted and pending invites」依賴第二個 team 的存在 | 0.75 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | 邏輯變更：pending invite 或 onboarding-v3 啟用時皆重導向至 personal/settings | 0.70 |
| 🔸 | Minor | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30` | 重複查詢 pending invite，可能造成不必要的資料庫負擔 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:584</code> hasPendingInviteByUserId 查詢條件錯誤：使用 accepted: true 而非 false</summary>

方法 `hasPendingInviteByUserId` 的實作中，Prisma 查詢條件為 `accepted: true`，但方法名稱與呼叫情境（檢查 pending invite）都應查詢 `accepted: false`。這會導致：
- 當使用者有 pending invite（accepted: false）時，方法回傳 false，onboarding 頁面不會重導向，功能失效。
- 當使用者有已接受的 membership 但無 pending invite 時，方法回傳 true，造成錯誤重導向。

建議修正為 `accepted: false`。

**判斷依據**：diff 中新增的方法實作，where 條件為 `accepted: true`，與方法名稱 `hasPendingInviteByUserId` 矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:23</code> 測試依賴既有資料，可能導致不穩定</summary>

在 `beforeAll` 中，測試會先尋找任意一個有 slug 的 team，若不存在才建立新 team。這使得測試結果依賴資料庫中既有的 team 資料，可能因環境不同而改變行為。例如，若既有 team 被刪除或修改，測試可能失敗。建議一律建立專屬的測試 team，並在 `afterAll` 清理。

**判斷依據**：測試程式碼中 `beforeAll` 的查詢邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試案例「should return true when user has both accepted and pending invites」依賴第二個 team 的存在</summary>

該測試會尋找另一個 team（`id: { not: testTeamId }`），若找不到則 `team2` 為 null，此時只建立 accepted membership，但預期結果為 `team2 ? true : false`，即 false。這使得測試在只有一個 team 的環境下會通過，但無法真正驗證「同時有 accepted 和 pending 時回傳 true」的情境。建議建立第二個 team 或改用其他方式確保測試覆蓋。

**判斷依據**：測試中尋找第二個 team 的邏輯，以及後續條件式建立 pending membership 與斷言。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> 邏輯變更：pending invite 或 onboarding-v3 啟用時皆重導向至 personal/settings</summary>

原本的邏輯是：只有當 `pendingInvite` 存在且 `onboardingV3Enabled` 為 true 時，才重導向至 `/onboarding/personal/settings`。修改後變成 `hasPendingInvite || onboardingV3Enabled`，這表示即使沒有 pending invite，只要 onboarding-v3 功能開啟，就會重導向至 personal/settings。這可能改變了原本的行為，需要確認是否符合預期。

**判斷依據**：diff 中條件式的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30</code> 重複查詢 pending invite，可能造成不必要的資料庫負擔</summary>

在 `ServerPage` 中直接呼叫 `MembershipRepository.hasPendingInviteByUserId`，但此頁面可能也會被 `checkOnboardingRedirect` 檢查（若該函式被用於 middleware 或其他地方），導致重複查詢。建議確認整體流程，避免不必要的查詢。

**判斷依據**：新增的查詢呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7613 (cache hit 7552) ｜ completion tokens 1417 ｜ PR #2</sub>