<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯抽成 MembershipRepository.hasPendingInviteByUserId，並在 onboarding getting-started 頁面新增伺服器端 redirect。主要風險在於新方法中 accepted 條件寫反（應為 false 卻寫成 true），導致行為與預期完全相反，且會讓已接受邀請的使用者被錯誤導向。此外，onboardingUtils.ts 中的條件由 AND 改為 OR，可能改變既有流程。測試涵蓋不足，未驗證新方法的實際查詢條件。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 的 accepted 條件寫反 | 0.99 |
| ⚠️ | Major | `packages/features/auth/lib/onboardingUtils.ts:69` | 條件由 AND 改為 OR 可能改變既有流程 | 0.80 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:44` | 測試未涵蓋 accepted: false 的實際查詢條件 | 0.75 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:1` | 測試資料清理不完整，可能殘留使用者 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 的 accepted 條件寫反</summary>

方法名稱是 hasPendingInviteByUserId，但查詢條件為 `accepted: true`，這會回傳「已接受」的邀請，而非「待處理」的邀請。這導致呼叫端（onboarding 頁面與 checkOnboardingRedirect）在用戶有已接受邀請時誤判為有 pending invite，進而錯誤 redirect。應改為 `accepted: false`。

**判斷依據**：diff 中新增的 static 方法內 where 條件為 accepted: true，與方法名稱及預期行為矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/auth/lib/onboardingUtils.ts:69</code> 條件由 AND 改為 OR 可能改變既有流程</summary>

原本只有在同時有 pending invite 且 onboarding-v3 啟用時才導向 personal/settings，現在改成任一條件成立即導向。若 onboarding-v3 啟用但用戶沒有 pending invite，原本會繼續其他流程，現在會直接導向 personal/settings。請確認此行為變更是否符合預期。

**判斷依據**：diff 中將 `if (pendingInvite && onboardingV3Enabled)` 改為 `if (hasPendingInvite || onboardingV3Enabled)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:44</code> 測試未涵蓋 accepted: false 的實際查詢條件</summary>

測試案例「should return true when user has a pending invite (accepted: false)」建立了一個 accepted: false 的 membership，但由於實作錯誤（accepted: true），此測試應會失敗。這表示測試並未有效驗證方法行為，且未直接測試查詢條件。建議修正實作後確保測試通過，並考慮增加直接驗證查詢條件的單元測試。

**判斷依據**：測試建立 accepted: false 的 membership，但實作查詢 accepted: true，測試應會失敗，顯示測試未有效防護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:1</code> 測試資料清理不完整，可能殘留使用者</summary>

在測試中若斷言失敗或發生例外，`prisma.user.delete` 可能不會被執行，導致測試資料殘留。建議使用 try/finally 或 afterEach 統一清理使用者。

**判斷依據**：多個測試在最後手動刪除使用者，但缺乏錯誤處理，若測試中途失敗可能殘留。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4607 (cache hit 1536) ｜ completion tokens 1008 ｜ PR #2</sub>