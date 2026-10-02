<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，讓功能可限定在 org、team 或 user 層級。主要風險在於 `listFeaturesForUser` 的過濾條件被反轉（`!state.globalEnabled`），會導致回傳未全域啟用的功能，造成使用者看到不應出現的選項。此外，`config.ts` 中新增了未使用的常數，違反 lint 規範。整體設計合理，但需修正上述問題後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件反轉，回傳未全域啟用的功能 | 0.95 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/featureOptIn/_router.ts:103` | setUserFeatureState 呼叫缺少 await | 0.80 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 的條件判斷可能顛倒 | 0.75 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:5` | [R06] 未使用的常數 UNUSED_CONSTANT 違反 lint 規範 | 0.90 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試中 mock isFeatureAllowedForScope 可能隱藏真實驗證 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件反轉，回傳未全域啟用的功能</summary>

在 `listFeaturesForUser` 中，原本應回傳 `globalEnabled` 為 true 的功能，但程式碼改為 `!state.globalEnabled`，導致回傳所有未全域啟用的功能。這會讓使用者在設定頁看到不應出現的功能，可能造成混淆或錯誤操作。

建議改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且註解仍寫著「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」，明顯矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/featureOptIn/_router.ts:103</code> setUserFeatureState 呼叫缺少 await</summary>

在 `setUserFeatureState` 的 mutation 中，呼叫 `featureOptInService.setUserFeatureState(...)` 時移除了 `await`。這會導致錯誤無法被捕捉，且回應可能在操作完成前就回傳。若服務內部拋出錯誤，tRPC 可能無法正確處理，造成未處理的 rejection。

建議加回 `await`。

**判斷依據**：diff 中此行由 `await featureOptInService.setUserFeatureState({` 改為 `featureOptInService.setUserFeatureState({`，且函式為 async。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 的條件判斷可能顛倒</summary>

在 `setUserFeatureState` 中，原本 `if (state === "inherit")` 的分支被改為 `if (state !== "inherit")`，但兩個分支的內容似乎沒有對調。這可能導致當 state 為 "inherit" 時執行錯誤的邏輯（例如嘗試讀取 `assignedBy`），而其他 state 則執行 inherit 的邏輯。

請確認此條件判斷是否正確，並檢查測試是否涵蓋此情境。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，但下方 else 分支仍保留原本 inherit 的處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:5</code> [R06] 未使用的常數 UNUSED_CONSTANT 違反 lint 規範</summary>

新增的 `UNUSED_CONSTANT` 常數未被使用，會觸發 Biome 的 unused 警告。根據規範 R06，lint 必須通過且警告視為錯誤，此常數應移除。

**判斷依據**：diff 中新增此行，且後續程式碼未引用此常數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試中 mock isFeatureAllowedForScope 可能隱藏真實驗證</summary>

在整合測試中，`isFeatureAllowedForScope` 被 mock 為永遠回傳 true，這可能導致測試無法驗證實際的 scope 驗證邏輯。雖然單元測試有涵蓋，但整合測試應盡量使用真實實作，以確保整體流程正確。

建議考慮移除 mock，或改用真實的 config 資料。

**判斷依據**：diff 中新增此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10807 (cache hit 10752) ｜ completion tokens 1284 ｜ PR #14</sub>