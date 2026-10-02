<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，讓功能可依 org/team/user 層級啟用。主要風險在於 `listFeaturesForUser` 的過濾條件被反轉（`!state.globalEnabled`），會導致回傳未全域啟用的功能；此外 `setUserFeatureState` 的條件判斷從 `state === "inherit"` 改為 `state !== "inherit"`，可能造成非 inherit 狀態的 assignedBy 處理錯誤。另有未使用的常數與測試中 mock 行為可能掩蓋真實問題。建議先修正這兩個邏輯錯誤再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件反轉，回傳未全域啟用的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件判斷反轉，非 inherit 狀態可能錯誤處理 assignedBy | 0.90 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試 mock isFeatureAllowedForScope 為 true，可能掩蓋 scope 驗證問題 | 0.70 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:5` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.test.ts:22` | 測試 mock 的 getOptInFeaturesForScope 回傳所有功能，可能與實際邏輯不符 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件反轉，回傳未全域啟用的功能</summary>

在 `listFeaturesForUser` 中，原本應回傳 `globalEnabled` 為 true 的功能，但此處改為 `!state.globalEnabled`，導致回傳所有未全域啟用的功能。這會讓使用者看到不應顯示的功能，且可能造成前端錯誤。

建議改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且註解仍寫「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件判斷反轉，非 inherit 狀態可能錯誤處理 assignedBy</summary>

原本邏輯為 `if (state === "inherit")` 時直接設定狀態，否則處理 `assignedBy`。此處改為 `if (state !== "inherit")`，導致當 state 為 "enabled" 或 "disabled" 時會進入第一個分支，但該分支只呼叫 `setUserFeatureState` 而未處理 `assignedBy`，可能造成資料不正確。

建議改回 `if (state === "inherit")`。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，且後續 else 分支處理 assignedBy 的邏輯未變。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試 mock isFeatureAllowedForScope 為 true，可能掩蓋 scope 驗證問題</summary>

在整合測試中，將 `isFeatureAllowedForScope` mock 為永遠回傳 true，這會使所有 scope 驗證失效，無法測試實際的 scope 限制。若整合測試的目的是驗證資料庫行為，應使用真實的 config 或明確設定 mock 回傳值，以確保 scope 邏輯被涵蓋。

建議移除 mock 或改為針對特定測試案例設定回傳值。

**判斷依據**：diff 中新增此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior.」

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:5</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 未被使用，且註解表明應被 lint 移除。這會觸發 lint 警告（R06），且增加程式碼噪音。

建議直接刪除此行。

**判斷依據**：diff 中新增此行，且無任何使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.test.ts:22</code> 測試 mock 的 getOptInFeaturesForScope 回傳所有功能，可能與實際邏輯不符</summary>

在單元測試中，`getOptInFeaturesForScope` 被 mock 為回傳所有功能，這使得測試無法驗證 scope 過濾邏輯。若測試目的是驗證 service 的行為，應使用真實的 config 或模擬不同 scope 的回傳值。

建議調整 mock 以反映實際的 scope 過濾。

**判斷依據**：diff 中新增此行，且 mockFeatures 包含所有功能，未依 scope 過濾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10807 (cache hit 1536) ｜ completion tokens 1389 ｜ PR #14</sub>