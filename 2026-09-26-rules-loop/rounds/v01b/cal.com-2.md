<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯從 onboardingUtils.ts 抽到 MembershipRepository，並在 getting-started 頁面新增伺服器端 redirect。主要風險在於 hasPendingInviteByUserId 的查詢條件寫反（accepted: true 應為 false），導致功能完全失效；此外，測試檔案存在資料清理不完整與相依於既有資料的問題。建議先修正查詢條件並補強測試隔離。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件寫反，永遠找不到 pending invite | 0.99 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:12` | 測試資料清理不完整，可能殘留 user 或 membership | 0.80 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試相依於資料庫中既有的第二個 team，可能不穩定 | 0.75 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | 邏輯變更可能導致 onboarding-v3 關閉時仍強制 redirect | 0.70 |
| 🔸 | Minor | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30` | 重複的 pending invite 檢查可能造成不必要的 DB 查詢 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件寫反，永遠找不到 pending invite</summary>

在 `hasPendingInviteByUserId` 中，`where` 條件使用 `accepted: true`，但方法名稱與用途是尋找「pending」邀請，應為 `accepted: false`。這會導致永遠回傳 `false`，使新增的 redirect 邏輯完全失效。

**失敗情境**：使用者有 pending invite 時，`hasPendingInviteByUserId` 回傳 `false`，不會觸發 redirect，使用者仍會停留在原本的 onboarding 頁面。

**建議修法**：將 `accepted: true` 改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 區塊的 `accepted: true` 與方法名稱 `hasPendingInviteByUserId` 矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:12</code> 測試資料清理不完整，可能殘留 user 或 membership</summary>

多個測試在建立 user 後，若中途斷言失敗或拋出例外，`afterEach` 只會刪除 `createdMembershipIds` 中的 membership，但不會刪除測試建立的 user。這會導致測試資料殘留在資料庫中，影響後續測試或環境。

**建議修法**：在 `afterEach` 中一併刪除測試建立的 user，或使用 transaction/rollback 機制。

**判斷依據**：測試中建立 user 後未記錄其 id，`afterEach` 僅刪除 membership，未刪除 user。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試相依於資料庫中既有的第二個 team，可能不穩定</summary>

在「should return true when user has both accepted and pending invites」測試中，使用 `prisma.team.findFirst` 尋找 id 不等於 `testTeamId` 的 team。若資料庫中沒有其他 team，`team2` 會是 null，測試會降級為只驗證 accepted membership 的情況，無法真正測試 mixed invites 的情境。

**建議修法**：在測試中建立第二個 team，或使用獨立的測試資料。

**判斷依據**：測試邏輯依賴外部資料，若無第二個 team 則測試覆蓋率不足。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> 邏輯變更可能導致 onboarding-v3 關閉時仍強制 redirect</summary>

原本的條件是 `pendingInvite && onboardingV3Enabled`，現在改為 `hasPendingInvite || onboardingV3Enabled`。這表示即使 `onboarding-v3` feature flag 關閉，只要有 pending invite 就會 redirect 到 `/onboarding/personal/settings`。這可能不是預期行為，因為舊版 onboarding 可能仍需要處理 pending invite。

**建議修法**：確認產品需求，若 pending invite 應獨立於 feature flag，則保留；否則應維持 `&&` 條件。

**判斷依據**：diff 中將 `&&` 改為 `||`，改變了 redirect 的觸發條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30</code> 重複的 pending invite 檢查可能造成不必要的 DB 查詢</summary>

在 `getting-started` 頁面新增了 `hasPendingInviteByUserId` 檢查，但 `checkOnboardingRedirect` 中也會進行相同檢查。若此頁面原本就會呼叫 `checkOnboardingRedirect`，則可能造成重複查詢。

**建議修法**：確認呼叫鏈，避免重複查詢，或將檢查結果傳遞。

**判斷依據**：diff 中新增的檢查與 `onboardingUtils.ts` 中的檢查重複。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6046 (cache hit 6016) ｜ completion tokens 1437 ｜ PR #2</sub>