<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了在 onboarding 頁面檢查待處理邀請並重新導向的邏輯，並將該檢查抽成 MembershipRepository 的靜態方法。主要風險在於 hasPendingInviteByUserId 的查詢條件寫反了（accepted: true 應為 false），導致功能完全失效；此外，靜態方法直接使用全域 prisma 實例，違反了 repository 的依賴注入模式，且測試中混用全域 prisma 與 repository 實例，可能造成資料不一致。建議先修正查詢條件，並考慮將方法改為實例方法以符合既有架構。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/membership/repositories/MembershipRepository.ts:584` | hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false | 0.99 |
| ⚠️ | Major | `packages/features/membership/repositories/MembershipRepository.ts:584` | 靜態方法直接使用全域 prisma 實例，違反 repository 依賴注入模式 | 0.80 |
| 🔸 | Minor | `packages/features/membership/repositories/MembershipRepository.integration-test.ts:3` | 測試檔案直接使用全域 prisma，與 repository 實例不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:584</code> hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false</summary>

此方法旨在檢查用戶是否有待處理的邀請（accepted: false），但查詢條件卻寫成 `accepted: true`，導致永遠找不到待處理邀請，回傳 false。這會使 PR 的核心功能（將有待處理邀請的用戶重新導向到個人 onboarding）完全失效。

建議將條件改為 `accepted: false`。

**判斷依據**：diff 中新增的 `hasPendingInviteByUserId` 方法內，`where` 條件為 `accepted: true`，但方法名稱與呼叫處的意圖皆為檢查 `accepted: false` 的邀請。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/membership/repositories/MembershipRepository.ts:584</code> 靜態方法直接使用全域 prisma 實例，違反 repository 依賴注入模式</summary>

此 repository 類別的其他方法皆透過建構子注入的 `this.prismaClient` 存取資料庫，但新增的 `hasPendingInviteByUserId` 為靜態方法，直接使用從 `@calcom/prisma` 匯入的全域 `prisma` 實例。這會造成：
1. 無法在測試中替換為 mock 或 transaction client。
2. 與類別既有的依賴注入模式不一致。

建議改為實例方法，並使用 `this.prismaClient`。

**判斷依據**：diff 中新增的方法宣告為 `static`，且方法內使用 `prisma.membership.findFirst`，而同一檔案中其他方法皆使用 `this.prismaClient`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/membership/repositories/MembershipRepository.integration-test.ts:3</code> 測試檔案直接使用全域 prisma，與 repository 實例不一致</summary>

測試中直接使用全域 `prisma` 來建立和刪除測試資料，而 `MembershipRepository` 若改為實例方法並注入 prisma client，測試應使用相同的 client 以確保資料一致性。目前測試通過是因為 repository 靜態方法也使用全域 prisma，但若修正上述依賴注入問題，此測試可能需要調整。

**判斷依據**：測試檔案開頭匯入全域 prisma，並在測試中使用它來操作資料庫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6046 (cache hit 6016) ｜ completion tokens 921 ｜ PR #2</sub>