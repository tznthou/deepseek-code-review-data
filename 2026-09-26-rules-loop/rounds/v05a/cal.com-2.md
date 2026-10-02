<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 在 onboarding 頁面新增了對 pending invites 的檢查，並將原本在 onboardingUtils 中的查詢邏輯抽到 MembershipRepository。主要風險在於 hasPendingInviteByUserId 的查詢條件寫反了（accepted: true 應為 accepted: false），導致功能完全失效；此外，onboardingUtils 中的條件判斷從 AND 改成 OR，可能造成非預期的重導向。測試檔案存在資料清理不完整與相依於既有資料的問題。建議先修正查詢條件與條件邏輯，再補強測試隔離。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件寫反，導致功能失效 | 0.99 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | 條件判斷從 AND 改為 OR，可能造成非預期重導向 | 0.85 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試相依於既有資料，可能導致不穩定 | 0.80 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:152` | 測試資料清理不完整，可能殘留 user 資料 | 0.70 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:1` | 測試檔案未遵循 R08 的 UTC 時區設定 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件寫反，導致功能失效</summary>

`hasPendingInviteByUserId` 的 `where` 條件使用 `accepted: true`，但方法名稱與用途是檢查「pending invite」（未接受的邀請），應該使用 `accepted: false`。這會導致所有使用者都被判定為沒有 pending invite，新增的 redirect 邏輯永遠不會觸發。

建議修正為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱與呼叫端（`onboardingUtils.ts` 與 `page.tsx`）的語意都是檢查 pending invite（未接受）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> 條件判斷從 AND 改為 OR，可能造成非預期重導向</summary>

原本的條件是 `pendingInvite && onboardingV3Enabled`，現在改成 `hasPendingInvite || onboardingV3Enabled`。這表示只要使用者有任何 pending invite，即使 onboarding-v3 feature flag 未啟用，也會被重導向到 `/onboarding/personal/settings`。這可能不是預期的行為，因為 onboarding-v3 可能包含其他必要的設定或流程。

建議確認此變更是否符合產品需求，或改回 `hasPendingInvite && onboardingV3Enabled`。

**判斷依據**：diff 中原本的 `if (pendingInvite && onboardingV3Enabled)` 被改為 `if (hasPendingInvite || onboardingV3Enabled)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試相依於既有資料，可能導致不穩定</summary>

在 `should return true when user has both accepted and pending invites` 測試中，使用 `prisma.team.findFirst` 尋找另一個 team（`id: { not: testTeamId }`）。如果資料庫中沒有其他 team，`team2` 會是 null，測試會變成只驗證 accepted membership 的情況，但期望值卻根據 `team2` 是否存在而改變，這使得測試的意圖不明確且可能誤報。

建議在測試中明確建立所需的第二個 team，並在測試後清理。

**判斷依據**：diff 中測試使用 `findFirst` 尋找既有 team，若不存在則 `team2` 為 null，後續邏輯會跳過建立 pending membership，但期望值卻依賴 `team2` 是否存在。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:152</code> 測試資料清理不完整，可能殘留 user 資料</summary>

在 `should return true when user has both accepted and pending invites` 測試中，最後呼叫 `await clearTestMemberships()` 後刪除 user，但 `clearTestMemberships` 只刪除 `createdMembershipIds` 中的 membership。如果測試中因為某些原因（例如 `team2` 不存在）沒有將 pending membership 加入 `createdMembershipIds`，但實際上建立了 pending membership，則該 membership 不會被清理，可能影響後續測試。

建議在測試中明確追蹤所有建立的資料，或使用交易或獨立的測試資料庫來確保隔離。

**判斷依據**：diff 中測試結尾的清理邏輯依賴 `createdMembershipIds`，但該陣列可能未包含所有建立的 membership。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:1</code> 測試檔案未遵循 R08 的 UTC 時區設定</summary>

測試檔案中使用了 `Date.now()` 來產生唯一的 email 和 username，但未明確設定時區。雖然 `Date.now()` 不受時區影響，但若測試中有其他時間相關邏輯，可能導致不一致。根據 R08，測試應在 UTC 時區下執行。

建議確認測試執行環境已設定 `TZ=UTC`，或避免在測試中使用時間相關的動態值。

**判斷依據**：diff 中測試檔案未包含時區設定，且使用了 `Date.now()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6015 (cache hit 4608) ｜ completion tokens 1474 ｜ PR #2</sub>