<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯從 onboardingUtils 抽到 MembershipRepository，並在 getting-started 頁面新增伺服器端 redirect。主要風險在於 `hasPendingInviteByUserId` 的查詢條件寫反了（`accepted: true` 應為 `accepted: false`），導致功能完全失效；此外，`checkOnboardingRedirect` 的條件從 `pendingInvite && onboardingV3Enabled` 改為 `hasPendingInvite || onboardingV3Enabled`，可能改變既有行為。測試檔案存在資料清理與相依性問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false | 0.99 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | checkOnboardingRedirect 條件變更可能導致非預期 redirect | 0.80 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:1` | 測試檔案違反 R08：未設定 UTC 時區 | 0.80 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:1` | 測試資料清理不完整，可能殘留 user 資料 | 0.70 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:23` | 測試相依於既有資料，可能不穩定 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false</summary>

此方法目的是檢查使用者是否有 pending invite（未接受的邀請），但查詢條件寫成 `accepted: true`，只會找到已接受的 membership，導致永遠回傳 false（除非使用者有已接受的 membership，但這與方法名稱和用途相反）。

**失敗情境**：使用者透過邀請連結註冊，系統建立一筆 `accepted: false` 的 membership，呼叫此方法應回傳 true 以觸發 redirect，但實際回傳 false，使用者不會被導向 personal onboarding。

**建議修法**：將 `accepted: true` 改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，與方法名稱及註解「pending invite」矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> checkOnboardingRedirect 條件變更可能導致非預期 redirect</summary>

原本邏輯為 `pendingInvite && onboardingV3Enabled`，只有當使用者有 pending invite 且 onboarding-v3 feature flag 開啟時才導向 personal settings。現在改為 `hasPendingInvite || onboardingV3Enabled`，只要 onboarding-v3 開啟，所有使用者都會被導向 personal settings，即使沒有 pending invite。

**失敗情境**：若 onboarding-v3 已全面啟用，所有新使用者（無 pending invite）都會被強制導向 personal settings，可能跳過原本的 getting-started 流程。

**建議修法**：確認此行為變更是否為預期。若不是，應保留 `&&` 條件；若是，請在 PR 描述中說明。

**判斷依據**：diff 中將 `if (pendingInvite && onboardingV3Enabled)` 改為 `if (hasPendingInvite || onboardingV3Enabled)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:1</code> 測試檔案違反 R08：未設定 UTC 時區</summary>

此測試檔案未設定 `process.env.TZ = 'UTC'` 或使用其他方式確保 UTC 時區。雖然目前測試內容未直接涉及時間，但根據規範 R08，所有測試必須使用 UTC 時區，以避免未來新增時間相關測試時出現問題。

**建議修法**：在測試檔案頂部加入 `process.env.TZ = 'UTC'` 或使用 Vitest 的 `setupFiles` 全域設定。

**判斷依據**：diff 新增的測試檔案中未見任何時區設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:1</code> 測試資料清理不完整，可能殘留 user 資料</summary>

多個測試案例在建立 user 後，若測試失敗或例外拋出，`prisma.user.delete` 可能不會被執行，導致測試資料殘留。此外，`createdMembershipIds` 陣列在部分測試中手動清空，但若測試中途失敗，後續 `afterEach` 可能無法正確清理。

**失敗情境**：測試因 assertion 失敗而中斷，user 和 membership 資料留在資料庫中，影響後續測試或汙染開發環境。

**建議修法**：使用 `try/finally` 確保清理，或將 user 建立與刪除也納入 `afterEach` 統一管理。

**判斷依據**：diff 中多處測試在建立 user 後直接刪除，但無例外保護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:23</code> 測試相依於既有資料，可能不穩定</summary>

`beforeAll` 中先尋找任意 team（`slug: { not: null }`），若不存在才建立新 team。這使得測試相依於資料庫中是否已有 team，且若既有 team 被其他測試刪除或修改，可能導致測試失敗。

**建議修法**：一律建立專屬測試 team，並在 `afterAll` 刪除，避免相依於既有資料。

**判斷依據**：diff 中 `beforeAll` 使用 `findFirst` 取得任意 team。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5231 (cache hit 5120) ｜ completion tokens 1484 ｜ PR #2</sub>