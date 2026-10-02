<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，讓功能可限定在 org/team/user 層級。主要風險在於 `listFeaturesForUser` 的過濾條件疑似寫反（應回傳 globalEnabled 為 true 的功能，但程式碼回傳 false 的），以及 `FeatureOptInService.ts` 中 `setUserFeatureState` 的條件判斷邏輯反轉，可能導致 inherit 狀態無法正確處理。此外，`config.ts` 中新增的 `UNUSED_CONSTANT` 違反 lint 規範，且測試中 mock 的 `isFeatureAllowedForScope` 可能造成測試與實際行為不一致。建議優先修正這兩個邏輯錯誤，並移除未使用的常數。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件寫反，導致回傳 globalEnabled 為 false 的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件判斷反轉，導致 inherit 狀態無法正確處理 | 0.90 |
| ⚠️ | Major | `packages/features/feature-opt-in/config.ts:4` | [R06] 新增未使用的常數 UNUSED_CONSTANT，違反 lint 規範 | 0.90 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 測試中 mock isFeatureAllowedForScope 為 true，可能掩蓋 scope 驗證問題 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.test.ts:22` | 測試中 mock 的 getOptInFeaturesForScope 回傳所有功能，可能與實際邏輯不符 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件寫反，導致回傳 globalEnabled 為 false 的功能</summary>

在 `listFeaturesForUser` 中，原本的過濾條件是 `.filter((state) => state.globalEnabled)`，但此次修改改成了 `.filter((state) => !state.globalEnabled)`。這會導致回傳的結果只包含全域停用的功能，而全域啟用的功能反而被排除。這與函式的文件說明（「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」）完全相反。

**失敗情境**：當使用者呼叫 `listFeaturesForUser` 時，所有全域啟用的功能都不會出現在結果中，而全域停用的功能卻會出現，造成前端顯示錯誤或使用者無法看到應有的功能。

**建議修法**：將條件改回 `.filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且函式註解仍寫著「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件判斷反轉，導致 inherit 狀態無法正確處理</summary>

在 `setUserFeatureState` 中，原本的邏輯是 `if (state === "inherit")` 執行 inherit 分支，否則執行一般設定。但此次修改將條件改為 `if (state !== "inherit")`，這會導致當 state 為 "inherit" 時，反而進入一般設定分支，而其他狀態（enabled/disabled）則進入 inherit 分支。這會造成行為完全相反。

**失敗情境**：當使用者嘗試將功能設為 inherit 時，程式會呼叫 `setUserFeatureState` 並帶入 `assignedBy`，但 `assignedBy` 可能不存在，導致執行錯誤；反之，當使用者嘗試設定 enabled/disabled 時，程式會執行 inherit 分支，忽略 `assignedBy`，造成權限設定錯誤。

**建議修法**：將條件改回 `if (state === "inherit")`。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，且後續分支邏輯未同步調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/config.ts:4</code> [R06] 新增未使用的常數 UNUSED_CONSTANT，違反 lint 規範</summary>

在 `config.ts` 中新增了 `const UNUSED_CONSTANT = "this-should-be-removed";`，但此常數從未被使用。根據 repo 規範 R06，pre-commit hook 會執行 `biome lint --error-on-warnings`，未使用的變數會觸發 warning 並被視為 error，導致 commit 失敗。此外，此常數名稱也暗示其本身不應存在。

**建議修法**：移除該常數。

**判斷依據**：diff 中新增了此常數，且後續程式碼未引用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 測試中 mock isFeatureAllowedForScope 為 true，可能掩蓋 scope 驗證問題</summary>

在 integration test 中，使用 `vi.mock` 將 `isFeatureAllowedForScope` 替換為永遠回傳 `true` 的函式。這會使得所有 scope 驗證在 integration test 中失效，即使實際程式碼的 scope 驗證有誤，測試仍會通過。這降低了測試的可靠性，無法捕捉 scope 相關的 bug。

**建議修法**：考慮在 integration test 中保留實際的 `isFeatureAllowedForScope` 邏輯，或至少針對特定 scope 設定不同的 mock 回傳值，以驗證不同情境。

**判斷依據**：diff 中新增了此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior.」

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.test.ts:22</code> 測試中 mock 的 getOptInFeaturesForScope 回傳所有功能，可能與實際邏輯不符</summary>

在 unit test 中，`getOptInFeaturesForScope` 被 mock 為回傳所有 mockFeatures，而沒有根據 scope 過濾。這可能導致測試無法驗證 `listFeaturesForTeam` 是否正確使用 scope 過濾功能。雖然測試中直接驗證了 `featureIds` 的內容，但若實際程式碼的 `getOptInFeaturesForScope` 有誤，測試仍可能通過。

**建議修法**：讓 mock 的 `getOptInFeaturesForScope` 根據傳入的 scope 回傳對應的功能，以更貼近實際行為。

**判斷依據**：diff 中新增了此 mock，且後續測試預期 `featureIds` 包含所有功能，未區分 scope。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10807 (cache hit 10752) ｜ completion tokens 1811 ｜ PR #14</sub>