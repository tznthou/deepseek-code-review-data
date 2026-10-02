<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯抽到 MembershipRepository，並在 onboarding getting-started 頁面加入伺服器端 redirect。主要風險在於 `hasPendingInviteByUserId` 的查詢條件寫成 `accepted: true`，與方法名稱及預期行為相反，會導致有 pending invite 的使用者不被 redirect，而沒有 pending invite 的使用者反而被 redirect。此外，測試檔案中對既有資料的依賴可能造成測試不穩定。建議先修正查詢條件並補強測試隔離。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:588` | hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false | 0.95 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:23` | 測試依賴既有資料庫中的 team，可能導致測試不穩定 | 0.80 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:128` | 測試中手動清理資料可能遺漏，導致後續測試受污染 | 0.75 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:158` | 測試名稱與實際行為不符：'should return true when user has both accepted and pending invites' 但條件依賴 tea | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:588</code> hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false</summary>

方法名稱為 `hasPendingInviteByUserId`，但查詢條件使用 `accepted: true`，這會回傳「已接受的邀請」而非「待處理的邀請」。這導致 `checkOnboardingRedirect` 中的判斷邏輯完全相反：沒有 pending invite 的使用者會被導向 `/onboarding/personal/settings`，而有 pending invite 的使用者不會被導向。

**失敗情境**：使用者註冊後沒有任何 pending invite（`accepted: true` 的 membership 不存在），`hasPendingInviteByUserId` 回傳 `false`，因此不會 redirect，使用者停留在 getting-started 頁面；反之，有 pending invite 的使用者（`accepted: false`）會被 redirect 到 personal settings，與預期相反。

**建議修法**：將 `accepted: true` 改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱與呼叫處（`checkOnboardingRedirect` 與 `ServerPage`）都預期檢查 pending invite（即 `accepted: false`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:23</code> 測試依賴既有資料庫中的 team，可能導致測試不穩定</summary>

`beforeAll` 中先以 `prisma.team.findFirst({ where: { slug: { not: null } } })` 尋找任意 team，若不存在才建立新 team。這使得測試結果依賴資料庫中是否已有 team，且若已有 team，其資料可能被其他測試或既有資料影響。

**失敗情境**：若資料庫中已存在一個 team，但該 team 的某些屬性（例如 slug 或 id）與測試假設不符，可能導致後續 membership 建立失敗或測試行為不一致。

**建議修法**：在 `beforeAll` 中一律建立專屬的測試 team，並在 `afterAll` 中刪除，避免依賴既有資料。

**判斷依據**：測試檔案第 15-17 行使用 `findFirst` 尋找任意 team，而非建立獨立測試資料。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:128</code> 測試中手動清理資料可能遺漏，導致後續測試受污染</summary>

多個測試在結束時手動刪除建立的 membership 和 user，但若測試中途失敗（例如 assertion 失敗），清理程式碼不會執行，可能留下殘留資料影響其他測試。

**失敗情境**：若 `expect(result).toBe(true)` 失敗，後面的 `prisma.membership.delete` 和 `prisma.user.delete` 不會執行，該 user 和 membership 會殘留在資料庫中，可能影響後續測試的 `findFirst` 結果。

**建議修法**：使用 `afterEach` 或 `try/finally` 確保清理必定執行，或使用測試資料庫交易回滾。

**判斷依據**：測試中在 assertion 之後手動刪除資料，若 assertion 失敗則清理不會執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:158</code> 測試名稱與實際行為不符：'should return true when user has both accepted and pending invites' 但條件依賴 team2 是否存在</summary>

測試名稱暗示應回傳 true，但實際期望值為 `team2 ? true : false`，若資料庫中沒有第二個 team，測試會期望 false，與名稱矛盾。

**失敗情境**：若資料庫中只有一個 team，`team2` 為 null，測試會期望 false，但測試名稱暗示應為 true，造成閱讀混淆。

**建議修法**：確保測試環境中一定有第二個 team，或調整測試名稱與邏輯一致。

**判斷依據**：測試名稱與期望值邏輯不一致，依賴 `team2` 是否存在。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6036 (cache hit 6016) ｜ completion tokens 1391 ｜ PR #2</sub>