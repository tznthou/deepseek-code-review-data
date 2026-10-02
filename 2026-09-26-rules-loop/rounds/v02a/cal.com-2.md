<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 在 onboarding 頁面新增了對待處理邀請的檢查，並將原本內嵌的 Prisma 查詢重構為 MembershipRepository 的靜態方法。主要風險在於 `hasPendingInviteByUserId` 的查詢條件寫反了（應為 `accepted: false` 而非 `accepted: true`），導致邏輯完全相反，可能將已接受邀請的使用者誤導至錯誤頁面。此外，整合測試的資料清理不完整，可能殘留測試資料。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件錯誤：應為 accepted: false | 0.99 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:60` | 測試資料清理不完整，可能殘留使用者資料 | 0.90 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試依賴既有資料，可能因環境而異 | 0.85 |
| 🔸 | Minor | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30` | 直接呼叫靜態方法，未使用依賴注入 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件錯誤：應為 accepted: false</summary>

此方法旨在檢查使用者是否有待處理的邀請，但查詢條件使用了 `accepted: true`，這會回傳已接受的邀請，導致回傳值與方法名稱相反。

**失敗情境**：當使用者有未接受的邀請時，此方法會回傳 `false`，導致 onboarding 頁面不會進行預期的重新導向；反之，當使用者只有已接受的邀請時，會回傳 `true`，造成錯誤的重新導向。

**建議修法**：將條件改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱與呼叫處的意圖皆為檢查「待處理」邀請（即 `accepted: false`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:60</code> 測試資料清理不完整，可能殘留使用者資料</summary>

在 `should return true when user has a pending invite (accepted: false)` 測試中，手動刪除了 membership 和 user，但未使用 `createdMembershipIds` 陣列進行統一清理，且若測試中途失敗，可能殘留資料。其他測試也有類似情況。

**建議修法**：統一使用 `afterEach` 中的 `clearTestMemberships` 清理 membership，並在 `afterAll` 或 `afterEach` 中刪除建立的 user。

**判斷依據**：測試中手動刪除資料，且未將 user 加入清理清單，若斷言失敗或例外拋出，可能殘留測試使用者。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試依賴既有資料，可能因環境而異</summary>

`should return true when user has both accepted and pending invites` 測試中，使用 `prisma.team.findFirst` 尋找第二個團隊，若資料庫中沒有其他團隊，則 `team2` 為 null，導致測試只驗證了 accepted 邀請的情況，未涵蓋 pending 邀請。

**建議修法**：在測試中建立第二個團隊，或使用獨立的測試資料，確保測試的確定性。

**判斷依據**：測試依賴資料庫中已存在的其他團隊，若不存在則測試分支不執行，無法完整驗證混合邀請情境。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30</code> 直接呼叫靜態方法，未使用依賴注入</summary>

在 ServerPage 中直接呼叫 `MembershipRepository.hasPendingInviteByUserId`，這使得測試和替換實作變得困難。建議透過依賴注入或使用 repository 實例。

**判斷依據**：此處直接使用靜態方法，與專案中其他 repository 的使用方式可能不一致，且不利於單元測試。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6046 (cache hit 1536) ｜ completion tokens 1161 ｜ PR #2</sub>