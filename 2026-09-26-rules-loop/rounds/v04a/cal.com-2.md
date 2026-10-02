<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯抽到 MembershipRepository，並在 onboarding getting-started 頁面加入伺服器端 redirect。主要風險在於 `hasPendingInviteByUserId` 的查詢條件寫反了（`accepted: true` 應為 `false`），導致功能完全失效；此外 `checkOnboardingRedirect` 的條件由 `pendingInvite && onboardingV3Enabled` 改為 `hasPendingInvite || onboardingV3Enabled`，可能造成未啟用 onboarding-v3 的使用者也被導向個人設定頁。測試檔案存在資料清理不完整與相依於既有資料的問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件寫反，應為 accepted: false | 0.98 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | 條件由 && 改為 \|\| 可能導致未啟用 onboarding-v3 的使用者被錯誤導向 | 0.85 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:45` | 測試資料清理不完整，可能殘留 user 或 membership | 0.80 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試相依於既有資料，可能因環境而失敗 | 0.70 |
| 🔸 | Minor | `apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30` | 重複的 pending invite 檢查可能造成不必要的資料庫查詢 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件寫反，應為 accepted: false</summary>

此方法名稱與用途是檢查是否有 pending invite（未接受的邀請），但查詢條件卻使用 `accepted: true`，這會回傳已接受的 membership，導致永遠無法偵測到 pending invite。

**失敗情境**：當使用者有未接受的團隊邀請時，此方法會回傳 `false`，因此不會觸發 redirect，使用者仍會停留在 getting-started 頁面，與 PR 目的相反。

**建議修法**：將 `accepted: true` 改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱與呼叫端（`checkOnboardingRedirect` 和 `page.tsx`）都預期是檢查 pending invite（未接受）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> 條件由 && 改為 || 可能導致未啟用 onboarding-v3 的使用者被錯誤導向</summary>

原本的條件是 `pendingInvite && onboardingV3Enabled`，表示只有當使用者有 pending invite 且啟用 onboarding-v3 時才導向個人設定頁。現在改為 `hasPendingInvite || onboardingV3Enabled`，這表示只要啟用 onboarding-v3，即使沒有 pending invite 也會被導向個人設定頁，可能跳過原本的 onboarding 流程。

**失敗情境**：若系統啟用 onboarding-v3，但使用者沒有 pending invite，原本應繼續進行 getting-started 流程，現在卻會被導向 `/onboarding/personal/settings`，造成流程中斷。

**建議修法**：確認此行為變更是否為預期。若僅想修正 pending invite 的檢查，應保留 `&&` 條件，僅將 `pendingInvite` 改為 `hasPendingInvite`。

**判斷依據**：diff 中將原本的 `if (pendingInvite && onboardingV3Enabled)` 改為 `if (hasPendingInvite || onboardingV3Enabled)`，改變了邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:45</code> 測試資料清理不完整，可能殘留 user 或 membership</summary>

在 `afterEach` 中只刪除 `createdMembershipIds` 中的 membership，但測試中建立的 user 並未被追蹤或刪除（除了在每個測試內手動刪除）。若測試中途失敗，user 會殘留在資料庫中。此外，`beforeAll` 中建立的 team 若原本不存在，會在 `afterAll` 刪除，但若測試中途失敗，`afterAll` 仍會執行，但 team 可能已被其他測試使用？

**失敗情境**：測試失敗時，資料庫會殘留測試 user，影響後續測試或開發環境。

**建議修法**：使用 `afterEach` 統一刪除所有建立的 user，或使用 transaction 包裹測試。

**判斷依據**：測試中多次呼叫 `prisma.user.create`，但沒有對應的清理機制，僅在每個測試內手動刪除，若測試失敗則會殘留。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試相依於既有資料，可能因環境而失敗</summary>

在 `should return true when user has both accepted and pending invites` 測試中，使用 `prisma.team.findFirst` 尋找另一個 team，若資料庫中沒有其他 team，則 `team2` 為 null，測試會降級為只驗證 accepted membership 的情況，無法真正測試 mixed invites。

**失敗情境**：在乾淨的測試資料庫中，此測試無法驗證同時有 accepted 和 pending invites 的情況。

**建議修法**：在測試中建立第二個 team，或使用 mock 資料。

**判斷依據**：測試依賴資料庫中已存在其他 team，否則無法建立 pending membership。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30</code> 重複的 pending invite 檢查可能造成不必要的資料庫查詢</summary>

此頁面新增了 `hasPendingInviteByUserId` 檢查，但 `checkOnboardingRedirect` 中也會進行相同檢查。若使用者已通過 `checkOnboardingRedirect` 的檢查，此處的檢查可能是多餘的，增加一次資料庫查詢。

**失敗情境**：效能影響輕微，但可考慮將檢查集中在一處。

**建議修法**：確認是否可移除其中一個檢查，或將邏輯整合。

**判斷依據**：diff 中新增了此檢查，而 `checkOnboardingRedirect` 也呼叫了相同方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5231 (cache hit 4480) ｜ completion tokens 1640 ｜ PR #2</sub>