<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯從 onboardingUtils.ts 抽到 MembershipRepository，並在 getting-started 頁面新增伺服器端 redirect。主要風險在於 hasPendingInviteByUserId 的查詢條件寫成 accepted: true，與方法名稱及預期行為相反，可能導致有 pending invite 的使用者被導向錯誤頁面，或無 pending invite 的使用者被誤導。此外，測試檔案中混用直接 prisma 操作與 repository 方法，且測試資料清理不完整，可能造成測試不穩定。建議先修正查詢條件並補強測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false | 0.95 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:82` | 測試資料清理不完整，可能影響其他測試 | 0.80 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試依賴既有資料，可能不穩定 | 0.70 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:1` | 測試檔案命名不符合專案慣例 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false</summary>

方法名稱為 `hasPendingInviteByUserId`，但查詢條件使用 `accepted: true`，這會回傳「已接受的邀請」而非「待處理的邀請」。這將導致：
1. 在 `onboardingUtils.ts` 中，原本的 `pendingInvite` 邏輯被取代後，有 pending invite 的使用者將不會被導向 `/onboarding/personal/settings`，除非他們同時有已接受的邀請。
2. 在 `getting-started/page.tsx` 中，有 pending invite 的使用者不會被 redirect，而沒有 pending invite 但已有 accepted membership 的使用者卻會被 redirect，行為完全相反。

建議將條件改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱與呼叫處的意圖都是檢查 pending invite（即 `accepted: false`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:82</code> 測試資料清理不完整，可能影響其他測試</summary>

在 `should return true when user has a pending invite (accepted: false)` 測試中，手動刪除 membership 後將 `createdMembershipIds` 清空，但使用者 `newUser` 是在測試內建立，若測試失敗（例如 assertion 失敗）則不會執行後續的刪除，導致使用者殘留。此外，`afterEach` 只清理 `createdMembershipIds` 中的 membership，不會清理使用者。建議將使用者建立與刪除也納入 `afterEach` 或使用 `try/finally` 確保清理。

**判斷依據**：測試中直接操作 prisma 進行清理，且未使用 `try/finally`，若測試失敗會留下測試資料。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試依賴既有資料，可能不穩定</summary>

在 `should return true when user has both accepted and pending invites` 測試中，使用 `prisma.team.findFirst` 尋找第二個 team，若資料庫中沒有其他 team，則 `team2` 為 null，測試會預期 `result` 為 false，但這並未真正測試「同時有 accepted 和 pending」的情境。建議在測試中建立第二個 team，或明確 skip 此測試若無第二個 team。

**判斷依據**：測試依賴資料庫中已存在其他 team，若不存在則測試情境不完整。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:1</code> 測試檔案命名不符合專案慣例</summary>

此測試檔案命名為 `MembershipRepository.integration-test.ts`，但專案中其他測試檔案可能使用 `.test.ts` 或 `.spec.ts` 後綴。建議確認專案慣例並調整命名。

**判斷依據**：檔案名稱使用 `.integration-test.ts`，可能與其他測試檔案命名不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6015 (cache hit 5888) ｜ completion tokens 1212 ｜ PR #2</sub>