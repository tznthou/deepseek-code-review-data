<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，讓功能可限定在 org/team/user 層級。主要風險在於 `listFeaturesForUser` 的過濾條件被反轉（`!state.globalEnabled`），會回傳全域停用的功能，且 `setUserFeatureState` 的條件判斷邏輯被改錯（`state !== "inherit"` 時才呼叫 repository），導致 enabled/disabled 狀態無法寫入。另外，`config.ts` 中新增了未使用的常數，違反 lint 規範。建議先修正這兩個邏輯錯誤再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件反轉，回傳全域停用的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件判斷錯誤，enabled/disabled 狀態無法寫入 | 0.95 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試中 mock isFeatureAllowedForScope 永遠回傳 true，可能掩蓋 scope 驗證問題 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:4` | [R06] 未使用的常數 UNUSED_CONSTANT 違反 lint 規範 | 0.90 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.test.ts:22` | 測試中 mock 的 getOptInFeaturesForScope 回傳所有功能，未反映 scope 過濾 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件反轉，回傳全域停用的功能</summary>

原本的程式碼是 `.filter((state) => state.globalEnabled)`，但這次修改將條件改為 `!state.globalEnabled`，導致只回傳全域停用的功能。這會讓使用者看不到任何應該顯示的 opt-in 功能，而看到不該顯示的功能。

**失敗情境**：當某個功能在全域設定中啟用時，使用者呼叫 `listFeaturesForUser` 將不會看到該功能；反之，若功能被停用，反而會出現在回傳結果中。

**建議修法**：將條件改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，邏輯明顯相反。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件判斷錯誤，enabled/disabled 狀態無法寫入</summary>

原本的邏輯是 `if (state === "inherit")` 時呼叫 `setUserFeatureState` 並傳入 `assignedBy`，否則呼叫另一個 overload。但這次修改將條件改為 `if (state !== "inherit")`，導致當 state 為 "enabled" 或 "disabled" 時，會進入 `else` 分支，而該分支預期 `input` 具有 `assignedBy` 屬性，但型別上並未保證，可能造成執行時期錯誤。

**失敗情境**：當使用者嘗試將功能設為 enabled 或 disabled 時，會進入錯誤的分支，可能拋出 `TypeError` 或寫入錯誤的資料。

**建議修法**：將條件改回 `if (state === "inherit")`。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，與預期邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試中 mock isFeatureAllowedForScope 永遠回傳 true，可能掩蓋 scope 驗證問題</summary>

在整合測試中，`isFeatureAllowedForScope` 被 mock 成永遠回傳 `true`，這使得整合測試無法驗證 scope 驗證邏輯是否正確。雖然註解說明 scope 驗證邏輯在單元測試中涵蓋，但整合測試應該驗證實際的 config 行為，否則可能遺漏 config 中 scope 設定錯誤的問題。

**建議修法**：考慮在整合測試中使用真實的 config，或至少針對特定 scope 設定不同的 mock 回傳值，以驗證整合路徑中的 scope 過濾。

**判斷依據**：diff 中新增了此 mock，且註解說明 scope 驗證邏輯在單元測試中測試。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:4</code> [R06] 未使用的常數 UNUSED_CONSTANT 違反 lint 規範</summary>

新增的 `UNUSED_CONSTANT` 常數未被使用，會觸發 Biome 的 `noUnusedVariables` 規則，且 pre-commit hook 設定為 `--error-on-warnings`，因此會阻擋 commit。

**建議修法**：移除該常數。

**判斷依據**：diff 中新增了未使用的常數，且註解也表明這是故意留下的。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.test.ts:22</code> 測試中 mock 的 getOptInFeaturesForScope 回傳所有功能，未反映 scope 過濾</summary>

在單元測試的 mock 中，`getOptInFeaturesForScope` 被設定為回傳所有 mock 功能，這使得測試無法驗證 `listFeaturesForTeam` 是否正確使用 scope 過濾。雖然有其他測試直接驗證 `isFeatureAllowedForScope`，但此處的 mock 可能掩蓋了 `listFeaturesForTeam` 中 scope 參數傳遞錯誤的問題。

**建議修法**：讓 mock 的 `getOptInFeaturesForScope` 根據傳入的 scope 回傳對應的功能，以更貼近真實行為。

**判斷依據**：diff 中新增了此 mock 設定，且未根據 scope 參數過濾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10776 (cache hit 9344) ｜ completion tokens 1623 ｜ PR #14</sub>