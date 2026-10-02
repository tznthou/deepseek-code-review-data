<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在修正使用邀請連結註冊的使用者被導向錯誤的 onboarding 頁面問題。主要變更包括：在 getting-started 頁面新增待處理邀請檢查、將 pending invite 查詢邏輯抽至 MembershipRepository、調整 checkOnboardingRedirect 的條件，以及新增整合測試。整體方向正確，但存在一個嚴重的邏輯錯誤：hasPendingInviteByUserId 方法查詢條件誤植為 accepted: true，導致功能完全失效。此外，測試中對既有團隊的依賴可能造成不穩定，且部分程式碼格式變更與 PR 目的無關。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false | 0.99 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | checkOnboardingRedirect 條件變更可能導致非預期行為 | 0.85 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:23` | 測試依賴既有團隊，可能導致不穩定 | 0.80 |
| 🔸 | Minor | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:5` | 不必要的格式變更 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false</summary>

此方法用於檢查使用者是否有待處理的邀請，但查詢條件卻設定為 `accepted: true`，這會導致永遠找不到待處理的邀請（因為待處理邀請的 accepted 為 false）。這使得 PR 的核心功能失效：使用者仍會被導向錯誤的頁面。

**失敗情境**：當使用者有 pending invite（accepted: false）時，`hasPendingInviteByUserId` 會回傳 false，導致 `checkOnboardingRedirect` 和 getting-started 頁面中的條件判斷錯誤，使用者不會被重新導向到 `/onboarding/personal/settings`。

**建議修法**：將 `accepted: true` 改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱和用途表明應查詢 pending invites（accepted: false）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> checkOnboardingRedirect 條件變更可能導致非預期行為</summary>

原本的條件是 `pendingInvite && onboardingV3Enabled`，現在改為 `hasPendingInvite || onboardingV3Enabled`。這表示即使沒有 pending invite，只要 `onboardingV3Enabled` 為 true，使用者就會被導向 `/onboarding/personal/settings`。這可能改變了原本的邏輯：原本只有在有 pending invite 且啟用 onboarding-v3 時才導向，現在只要啟用 onboarding-v3 就會導向。

**失敗情境**：如果系統啟用了 onboarding-v3，但使用者沒有 pending invite，原本可能應該走其他 onboarding 流程，現在卻會被強制導向 personal settings，可能造成流程中斷或錯誤。

**建議修法**：確認此變更是否符合預期。若原本邏輯正確，應保留 `&&`；若確實需要 `||`，請在 PR 描述中說明原因。

**判斷依據**：diff 中將 `if (pendingInvite && onboardingV3Enabled)` 改為 `if (hasPendingInvite || onboardingV3Enabled)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:23</code> 測試依賴既有團隊，可能導致不穩定</summary>

在 `beforeAll` 中，測試會先嘗試尋找一個既有團隊（`slug` 不為 null），若找不到才建立新團隊。這使得測試結果依賴資料庫中是否已存在符合條件的團隊，可能導致測試在不同環境下行為不一致。

**失敗情境**：如果資料庫中已存在一個團隊，但該團隊的設定或狀態影響測試（例如團隊已刪除或權限變更），測試可能失敗或產生非預期結果。

**建議修法**：在 `beforeAll` 中一律建立專屬的測試團隊，並在 `afterAll` 中刪除，以確保測試隔離性。

**判斷依據**：測試程式碼中先查詢既有團隊，若存在則使用，否則才建立新團隊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:5</code> 不必要的格式變更</summary>

此 PR 中包含了多處純格式變更（例如 import 順序調整、單引號改為雙引號、程式碼換行），這些變更與 PR 目的無關，可能增加 review 噪音。

**建議修法**：將格式變更與功能變更分開提交，或避免不必要的格式調整。

**判斷依據**：diff 中 import 順序被重新排列，且 `userEmail` 的引號從雙引號改為單引號。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4571 (cache hit 1408) ｜ completion tokens 1340 ｜ PR #2</sub>