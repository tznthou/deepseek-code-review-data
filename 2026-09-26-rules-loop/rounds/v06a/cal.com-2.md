<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查從 onboardingUtils 抽到 MembershipRepository，並在 getting-started 頁面新增伺服器端重導向。主要風險在於 `hasPendingInviteByUserId` 的條件寫反了（`accepted: true` 應為 `accepted: false`），導致行為完全相反；此外測試中對既有 team 的依賴可能造成不穩定。建議先修正條件再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 條件寫反，應查 accepted: false | 0.99 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:23` | 測試依賴既有 team，可能因資料狀態不穩定 | 0.80 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:121` | 測試中手動清理資料，可能遺漏或重複刪除 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 條件寫反，應查 accepted: false</summary>

方法名稱是 `hasPendingInviteByUserId`，但查詢條件使用 `accepted: true`，這會回傳「已接受的邀請」而非「待處理的邀請」。

**失敗情境**：
- 使用者有 pending invite（accepted: false）時，此方法回傳 `false`，導致 `getting-started` 頁面不會重導向，使用者卡在錯誤的 onboarding 流程。
- 使用者只有已接受的邀請時，此方法回傳 `true`，導致不必要的重導向。

**建議修法**：
將條件改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，與方法名稱及預期行為矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:23</code> 測試依賴既有 team，可能因資料狀態不穩定</summary>

`beforeAll` 中先以 `prisma.team.findFirst({ where: { slug: { not: null } } })` 尋找任意 team，若找不到才建立新 team。這使得測試結果依賴資料庫中既有的 team 資料，可能因其他測試或種子資料而變動。

**失敗情境**：
- 若資料庫中已存在多個 team，測試會使用第一個找到的 team，其狀態可能影響測試結果（例如 team 被刪除或欄位不符）。
- 若並行執行測試，可能互相干擾。

**建議修法**：
在 `beforeAll` 中一律建立專屬的測試 team，並在 `afterAll` 中刪除，避免依賴既有資料。

**判斷依據**：diff 中 `beforeAll` 使用 `findFirst` 而非 `create`，且未過濾特定條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:121</code> 測試中手動清理資料，可能遺漏或重複刪除</summary>

測試中多次手動呼叫 `prisma.membership.delete` 和 `prisma.user.delete`，並手動重置 `createdMembershipIds`。若測試中途失敗，可能留下殘留資料，影響後續測試。

**建議修法**：
統一使用 `afterEach` 清理，並在 `afterAll` 中刪除建立的 user 和 team，避免手動清理。

**判斷依據**：diff 中多處出現手動刪除與陣列重置，未完全依賴 `afterEach`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6036 (cache hit 4480) ｜ completion tokens 997 ｜ PR #2</sub>