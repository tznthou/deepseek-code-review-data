<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 將 pending invite 的檢查抽成 MembershipRepository.hasPendingInviteByUserId，並在 onboarding getting-started 頁面加入伺服器端 redirect。主要風險在於新方法實作中 accepted 條件寫反（應為 false 卻寫成 true），導致邏輯完全相反；此外測試檔案有資料清理不完整的問題，且測試中對 team2 的依賴可能造成 flaky。建議先修正 accepted 條件再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 的 accepted 條件寫反，導致邏輯完全相反 | 0.99 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | checkOnboardingRedirect 的條件邏輯變更可能造成非預期 redirect | 0.95 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:158` | 測試資料清理不完整，可能污染其他測試 | 0.90 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:1` | 測試檔案未遵循專案規範 R08：應使用 UTC 時區 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 的 accepted 條件寫反，導致邏輯完全相反</summary>

方法名稱是 hasPendingInviteByUserId，但查詢條件使用 `accepted: true`，這會回傳「已接受邀請」的 membership，而不是「待處理邀請」。這使得呼叫端（onboarding 頁面與 checkOnboardingRedirect）的判斷完全相反：沒有 pending invite 的使用者會被誤導到 personal onboarding，而有 pending invite 的使用者反而會繼續原本流程。

建議將條件改為 `accepted: false`。

**判斷依據**：diff 中新增的 static 方法內 where 條件為 `accepted: true`，與方法名稱及預期行為矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> checkOnboardingRedirect 的條件邏輯變更可能造成非預期 redirect</summary>

原本只有在 `pendingInvite && onboardingV3Enabled` 時才 redirect 到 personal settings；現在改成 `hasPendingInvite || onboardingV3Enabled`，這表示只要 onboarding-v3 feature flag 開啟，所有使用者都會被 redirect，即使沒有 pending invite。這可能不是預期行為，且會影響所有呼叫此函式的地方。

請確認此變更是否為刻意設計；若不是，應保留原本的 AND 條件。

**判斷依據**：diff 中將 `if (pendingInvite && onboardingV3Enabled)` 改為 `if (hasPendingInvite || onboardingV3Enabled)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:158</code> 測試資料清理不完整，可能污染其他測試</summary>

在 `should return true when user has both accepted and pending invites` 測試中，若 `team2` 不存在，則只建立 accepted membership，但測試期望值為 `false`（因為 `team2 ? true : false`），這會通過但實際上沒有測到 pending invite 的情境。此外，測試中建立的 user 在最後有刪除，但若測試中途失敗，user 可能殘留。建議使用 try/finally 或 afterEach 統一清理，並確保測試不依賴資料庫中是否已有其他 team。

**判斷依據**：測試邏輯依賴 `team2` 是否存在，且清理邏輯分散，容易造成資料殘留。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:1</code> 測試檔案未遵循專案規範 R08：應使用 UTC 時區</summary>

專案規範 R08 要求所有測試使用 Vitest 並設定 TZ=UTC。此測試檔案使用 Vitest 語法，但未見設定 UTC 時區的程式碼或指令。若測試中涉及時間相關邏輯（目前沒有），可能導致 flaky。建議在測試設定中統一處理時區。

**判斷依據**：測試檔案未包含時區設定，且專案規範明確要求。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6056 (cache hit 4480) ｜ completion tokens 1056 ｜ PR #2</sub>