<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 功能新增了 scope 設定（org/team/user），並在服務層加入對應的驗證邏輯。主要風險在於 `listFeaturesForUser` 的過濾條件被反轉（`!state.globalEnabled`），這會導致回傳未全域啟用的功能，屬於 blocker 等級的邏輯錯誤。此外，`config.ts` 中新增了一個未使用的常數，可能違反 lint 規則。整體而言，scope 驗證的設計合理，但需修正上述問題後才能合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件反轉，回傳未全域啟用的功能 | 0.98 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:5` | [R06] 未使用的常數 UNUSED_CONSTANT 可能觸發 lint 警告 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件反轉，回傳未全域啟用的功能</summary>

在 `listFeaturesForUser` 中，原本應回傳 `globalEnabled` 為 true 的功能，但程式碼改為 `!state.globalEnabled`，導致回傳未全域啟用的功能。這會讓使用者看到不應顯示的功能，可能造成混淆或錯誤操作。

建議改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，邏輯相反。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:5</code> [R06] 未使用的常數 UNUSED_CONSTANT 可能觸發 lint 警告</summary>

新增的 `UNUSED_CONSTANT` 未被使用，若 lint 設定將未使用變數視為警告，則會違反 R06（lint 警告視為錯誤）。建議移除該常數。

**判斷依據**：diff 中新增此行，且後續程式碼未使用此常數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10797 (cache hit 10752) ｜ completion tokens 568 ｜ PR #14</sub>