<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 功能新增了 scope 設定，允許在 org、team、user 三個層級分別控制功能可用性。主要變更包括：新增 scope 型別與相關常數、修改服務層以根據 scope 過濾功能並在設定狀態時驗證 scope、更新 UI 以使用新的常數，以及新增對應的單元測試。整體設計合理，但存在一個明確的邏輯錯誤：`listFeaturesForUser` 的過濾條件從 `state.globalEnabled` 改成了 `!state.globalEnabled`，這會導致只回傳全域停用的功能，與預期行為完全相反。此外，`config.ts` 中有一個未使用的常數 `UNUSED_CONSTANT`，雖然影響不大，但應移除。建議修正這兩個問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件邏輯錯誤 | 0.99 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:4` | 未使用的常數 UNUSED_CONSTANT | 0.95 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件邏輯錯誤</summary>

在 `listFeaturesForUser` 方法中，原本的過濾條件是 `state.globalEnabled`，但此 PR 將其改為 `!state.globalEnabled`。這會導致只回傳全域停用的功能，而全域啟用的功能反而被排除。這與方法的文件說明「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」完全相反。

**失敗情境**：當使用者呼叫此方法時，所有全域啟用的功能都不會出現在結果中，而全域停用的功能卻會出現。這將導致使用者介面顯示錯誤的功能列表，或讓使用者無法看到應該可用的功能。

**建議修法**：將條件改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且方法註解明確指出應回傳 globally enabled 的功能。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:4</code> 未使用的常數 UNUSED_CONSTANT</summary>

新增的常數 `UNUSED_CONSTANT` 沒有被任何地方使用，且其名稱暗示這是故意留下的未使用程式碼。這會觸發 lint 警告（如 no-unused-vars），並增加不必要的維護負擔。

**建議修法**：移除該常數及其註解。

**判斷依據**：diff 中新增了此常數，但後續程式碼中未見任何引用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9368 (cache hit 1536) ｜ completion tokens 748 ｜ PR #14</sub>