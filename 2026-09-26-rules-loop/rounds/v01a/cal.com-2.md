<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯從 onboardingUtils 抽到 MembershipRepository，並在 getting-started 頁面加入伺服器端 redirect。主要風險在於 hasPendingInviteByUserId 的查詢條件寫成 accepted: true，與方法名稱及預期行為相反，會導致有 pending invite 的使用者不被導向個人 onboarding，且 onboardingUtils 中的條件由 AND 改為 OR，可能造成未受邀使用者也被導向個人 onboarding。此外，測試檔案有資源清理與相依性問題。建議先修正查詢條件與條件邏輯，再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false | 0.98 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | 條件由 AND 改為 OR 可能導致未受邀使用者被導向個人 onboarding | 0.90 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:8` | 測試使用全域變數追蹤建立資源，可能導致測試間互相干擾 | 0.85 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:23` | 測試依賴資料庫中已存在的 team，可能因環境而異 | 0.80 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:122` | 測試中手動刪除 membership 後又呼叫 clearTestMemberships，可能造成重複刪除 | 0.70 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:145` | 測試中建立 user 後未在 finally 中刪除，可能殘留資料 | 0.70 |
| 🔸 | Minor | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30` | 直接呼叫靜態方法可能不利於測試與依賴注入 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false</summary>

方法名稱為 `hasPendingInviteByUserId`，但查詢條件使用 `accepted: true`，這會回傳「已接受邀請」的 membership，而非 pending（未接受）。這將導致有 pending invite 的使用者被誤判為沒有 pending invite，從而不會被導向個人 onboarding，與 PR 目的相反。

**失敗情境**：使用者透過邀請連結註冊，系統建立一筆 `accepted: false` 的 membership。當使用者進入 `/onboarding/getting-started` 時，此方法回傳 `false`，因此不會 redirect 到 `/onboarding/personal/settings`，使用者會停留在錯誤的 onboarding 頁面。

**建議修法**：將 `accepted: true` 改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱與 PR 描述皆表明應查詢 pending invites（`accepted: false`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> 條件由 AND 改為 OR 可能導致未受邀使用者被導向個人 onboarding</summary>

原本的條件是 `pendingInvite && onboardingV3Enabled`，表示只有當使用者有 pending invite 且 onboarding-v3 feature flag 啟用時才導向個人 onboarding。現在改為 `hasPendingInvite || onboardingV3Enabled`，這表示只要 onboarding-v3 啟用，即使使用者沒有任何 pending invite，也會被導向個人 onboarding。這可能不是預期行為，因為 onboarding-v3 可能只是啟用新的 onboarding 流程，但不一定所有使用者都應該走個人 onboarding。

**失敗情境**：假設 onboarding-v3 啟用，且使用者沒有 pending invite，原本應停留在團隊 onboarding 或預設頁面，但現在會被導向個人 onboarding，造成流程錯誤。

**建議修法**：確認產品需求。若個人 onboarding 僅適用於有 pending invite 的使用者，應保留 AND 條件；若 onboarding-v3 啟用時所有使用者都應走個人 onboarding，則此變更合理，但需確認。

**判斷依據**：diff 中將 `if (pendingInvite && onboardingV3Enabled)` 改為 `if (hasPendingInvite || onboardingV3Enabled)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:8</code> 測試使用全域變數追蹤建立資源，可能導致測試間互相干擾</summary>

測試檔案使用全域變數 `createdMembershipIds`、`testTeamId`、`createdTeamId` 來追蹤建立的資源，並在 `afterEach` 中清理 memberships，在 `afterAll` 中刪除 team。然而，若測試中途失敗，`afterEach` 可能不會執行，導致後續測試受到殘留資料影響。此外，`testTeamId` 在 `beforeAll` 中設定，但若 `beforeAll` 失敗，後續測試會使用未定義的 `testTeamId`。

**建議修法**：使用 `beforeEach` 建立測試所需的 team 和 user，並在 `afterEach` 中刪除，避免依賴全域狀態。或使用測試資料庫交易回滾。

**判斷依據**：測試檔案開頭定義了全域變數，並在多個測試中共享。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:23</code> 測試依賴資料庫中已存在的 team，可能因環境而異</summary>

在 `beforeAll` 中，測試會先尋找一個 `slug` 不為 null 的 team，若找不到才建立新的。這使得測試依賴於資料庫中是否已有 team，可能導致測試在不同環境下行為不一致。此外，若找到的 team 被其他測試使用，可能會互相影響。

**建議修法**：在 `beforeAll` 中一律建立專用的測試 team，並在 `afterAll` 中刪除，確保測試隔離。

**判斷依據**：測試中先查詢現有 team，若不存在才建立。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:122</code> 測試中手動刪除 membership 後又呼叫 clearTestMemberships，可能造成重複刪除</summary>

在 `should return true when user has a pending invite` 測試中，先手動刪除 membership，然後將 `createdMembershipIds.length = 0`，接著在 `afterEach` 中又呼叫 `clearTestMemberships`。由於 `createdMembershipIds` 已被清空，`clearTestMemberships` 不會執行任何刪除，但這樣的手動清理方式容易出錯。

**建議修法**：統一使用 `afterEach` 清理，不要在測試內手動刪除。

**判斷依據**：測試內手動刪除並清空陣列，與 `afterEach` 的清理邏輯重疊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:145</code> 測試中建立 user 後未在 finally 中刪除，可能殘留資料</summary>

多個測試在建立 user 後，若斷言失敗或發生例外，可能不會執行到刪除 user 的程式碼，導致測試資料殘留。

**建議修法**：使用 `try...finally` 或在 `afterEach` 中統一刪除建立的 user。

**判斷依據**：測試中建立 user 後，刪除動作在測試結尾，若中途失敗則不會執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30</code> 直接呼叫靜態方法可能不利於測試與依賴注入</summary>

`MembershipRepository.hasPendingInviteByUserId` 是靜態方法，直接使用全域 `prisma` 實例。這使得在單元測試中難以 mock，且與 repository 通常使用實例方法的模式不一致。

**建議修法**：考慮改為實例方法，並透過依賴注入傳入 prisma client。

**判斷依據**：在 page.tsx 中直接呼叫靜態方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6046 (cache hit 4480) ｜ completion tokens 2144 ｜ PR #2</sub>