<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯抽到 MembershipRepository，並在 onboarding getting-started 頁面新增伺服器端 redirect。主要風險在於 `hasPendingInviteByUserId` 的查詢條件寫成 `accepted: true`，與方法名稱及預期行為相反，會導致有 pending invite 的使用者不被導向個人 onboarding，反而被導向團隊 onboarding，造成流程錯誤。此外，測試檔案中直接使用全域 `prisma` 而非注入的 client，且測試資料清理不完整，可能影響其他測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false | 0.98 |
| ⚠️ | Major | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30` | 直接呼叫靜態方法，未使用依賴注入，可能造成測試困難 | 0.90 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:3` | 測試檔案直接使用全域 prisma，未遵循 repository 依賴注入模式 | 0.85 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:1` | 測試資料清理不完整，可能殘留使用者資料 | 0.80 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:23` | 測試依賴資料庫中既有的 team，可能因環境而異 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false</summary>

方法名稱為 `hasPendingInviteByUserId`，但查詢條件使用 `accepted: true`，這會回傳使用者是否有已接受的 membership，而非是否有 pending invite。這會導致在 `checkOnboardingRedirect` 中，有 pending invite 的使用者不會被導向 `/onboarding/personal/settings`，反而沒有 pending invite 的使用者會被錯誤導向。

**失敗情境**：使用者註冊後有 pending team invite（accepted: false），呼叫此方法會回傳 false，因此不會觸發 redirect，使用者會繼續進行團隊 onboarding，而非個人 onboarding。

**建議修法**：將 `accepted: true` 改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，where 條件為 `accepted: true`，與方法名稱及預期行為矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30</code> 直接呼叫靜態方法，未使用依賴注入，可能造成測試困難</summary>

在 ServerPage 中直接呼叫 `MembershipRepository.hasPendingInviteByUserId`，此靜態方法內部使用全域 `prisma`，而非透過 constructor 注入的 client。這使得單元測試難以 mock，且與專案中其他 repository 的使用方式不一致（其他方法多為 instance method，使用注入的 `prismaClient`）。

**建議修法**：將此方法改為 instance method，並在 ServerPage 中建立 repository instance（例如 `const membershipRepository = new MembershipRepository(prisma)`）後呼叫。

**判斷依據**：diff 中新增的呼叫直接使用靜態方法，而該方法在 repository 檔案中定義為 static，且內部使用全域 `prisma`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:3</code> 測試檔案直接使用全域 prisma，未遵循 repository 依賴注入模式</summary>

測試檔案中直接 import `prisma` 並用於建立測試資料，但 `MembershipRepository` 的 instance 方法通常接受注入的 `prismaClient`。此測試並未測試 repository 的 instance 方法，而是測試靜態方法，且靜態方法內部使用全域 `prisma`，這使得測試與實際使用情境脫節。

**建議修法**：若將 `hasPendingInviteByUserId` 改為 instance method，則測試應建立 repository instance 並注入測試用的 prisma client（或 mock）。

**判斷依據**：測試檔案中直接 import 全域 prisma，且測試的靜態方法內部也使用全域 prisma。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:1</code> 測試資料清理不完整，可能殘留使用者資料</summary>

在 `hasPendingInviteByUserId` 的測試中，每個測試都會建立新使用者，但只有在部分測試中明確刪除使用者。例如第一個測試在刪除 membership 後刪除使用者，但第二個測試在刪除 membership 後未刪除使用者，第三個測試也未刪除使用者。這可能導致測試資料殘留，影響其他測試或後續執行。

**建議修法**：在 `afterEach` 中統一清理所有建立的測試資料，包括使用者和 membership。

**判斷依據**：測試中對使用者的刪除不一致，部分測試未刪除使用者。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:23</code> 測試依賴資料庫中既有的 team，可能因環境而異</summary>

`beforeAll` 中先尋找既有 team（`slug` 不為 null），若找不到才建立新 team。這使得測試依賴資料庫狀態，若資料庫中沒有符合條件的 team，則會建立新 team，但若有多個 team，可能選到非預期的 team。此外，測試中第二個測試使用 `testTeamId`，但若 `beforeAll` 建立的 team 在測試中被刪除，可能導致外鍵錯誤。

**建議修法**：在測試中一律建立專屬的測試 team，並在 `afterAll` 中刪除，避免依賴既有資料。

**判斷依據**：測試中尋找既有 team 的邏輯可能導致測試不穩定。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6056 (cache hit 6016) ｜ completion tokens 1532 ｜ PR #2</sub>