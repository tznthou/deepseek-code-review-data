<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 pending invite 的檢查邏輯抽取到 MembershipRepository 的靜態方法，並在 onboarding 頁面新增對 pending invite 的 redirect。主要風險在於 `hasPendingInviteByUserId` 的查詢條件寫成 `accepted: true`，與方法名稱及預期行為相反，會導致 redirect 邏輯失效。此外，測試檔案存在資料清理與相依性問題，可能影響測試穩定性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:584` | hasPendingInviteByUserId 查詢條件錯誤：應為 accepted: false | 0.99 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:70` | 測試資料清理不完整，可能影響其他測試 | 0.90 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:127` | 測試依賴外部資料，可能因缺少第二個 team 而失敗 | 0.85 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:1` | 測試檔案缺少 import 順序整理 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:584</code> hasPendingInviteByUserId 查詢條件錯誤：應為 accepted: false</summary>

方法名稱為 `hasPendingInviteByUserId`，但查詢條件使用 `accepted: true`，這會導致方法回傳 `true` 僅當使用者有已接受的 membership，而非 pending invite。這會使 `checkOnboardingRedirect` 中的 `if (hasPendingInvite || onboardingV3Enabled)` 條件判斷錯誤，可能將沒有 pending invite 的使用者導向 `/onboarding/personal/settings`，或未將有 pending invite 的使用者導向正確頁面。

建議修正：
```ts
where: {
  userId,
  accepted: false,
},
```

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法，其 `where` 條件為 `accepted: true`，與方法名稱及預期行為矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:70</code> 測試資料清理不完整，可能影響其他測試</summary>

在 `should return true when user has a pending invite (accepted: false)` 測試中，手動刪除 membership 和 user 後，將 `createdMembershipIds` 陣列清空，但未使用 `clearTestMemberships` 函式。若測試中途失敗，可能殘留資料。建議統一使用 `clearTestMemberships` 並在 `afterEach` 中清理，避免手動管理。

**判斷依據**：測試中直接刪除 membership 並清空陣列，而非依賴 `afterEach` 的 `clearTestMemberships`，增加資料殘留風險。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:127</code> 測試依賴外部資料，可能因缺少第二個 team 而失敗</summary>

在 `should return true when user has both accepted and pending invites` 測試中，使用 `prisma.team.findFirst` 尋找第二個 team，若資料庫中沒有其他 team，則 `team2` 為 null，測試會跳過 pending membership 的建立，導致 `expect(result).toBe(team2 ? true : false)` 在 `team2` 為 null 時預期 `false`，但實際可能因其他因素回傳 `true`，造成測試不穩定。建議在測試中建立獨立的第二個 team，或明確處理缺少 team 的情況。

**判斷依據**：測試依賴資料庫中已存在的其他 team，若不存在則測試邏輯不完整。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:1</code> 測試檔案缺少 import 順序整理</summary>

import 順序未依專案慣例分組，可能觸發 lint 規則。建議依照專案現有 import 排序方式調整。

**判斷依據**：import 未依字母或類型分組，與其他檔案風格不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4571 (cache hit 4480) ｜ completion tokens 1232 ｜ PR #2</sub>