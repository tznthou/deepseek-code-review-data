<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 功能新增了 scope 設定，允許功能在 org、team、user 三個層級分別啟用。主要變更包括：新增 scope 型別與相關輔助函式、修改服務層以根據 scope 過濾功能、更新 UI 以使用新的常數，以及新增測試。整體方向合理，但存在一個明確的邏輯錯誤（listFeaturesForUser 的過濾條件相反），可能導致使用者看不到任何功能；此外，測試中對 isFeatureAllowedForScope 的 mock 方式可能導致測試無法正確驗證 scope 邏輯。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件相反，導致使用者看不到任何功能 | 0.95 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.test.ts:10` | 測試中 mock isFeatureAllowedForScope 的方式可能導致 scope 驗證未被正確測試 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:4` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件相反，導致使用者看不到任何功能</summary>

在 `listFeaturesForUser` 方法中，原本的過濾條件是 `.filter((state) => state.globalEnabled)`，但此次變更將其改為 `.filter((state) => !state.globalEnabled)`。這會導致只回傳全域停用的功能，而使用者應該看到的是全域啟用的功能。這是一個明顯的邏輯錯誤，會讓使用者無法看到任何可用的 opt-in 功能。

建議修正：將 `!state.globalEnabled` 改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由原本的 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且方法註解仍說明「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」，與實作矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.test.ts:10</code> 測試中 mock isFeatureAllowedForScope 的方式可能導致 scope 驗證未被正確測試</summary>

在測試檔案中，`isFeatureAllowedForScope` 被 mock 成一個可變的函式，並在 `beforeEach` 中設定為回傳 `true`。然而，在 `setUserFeatureState` 和 `setTeamFeatureState` 的測試中，有些測試會將 mock 回傳值改為 `false` 來驗證錯誤拋出，但其他測試則依賴預設的 `true`。這種方式可能導致測試之間互相影響，且無法完全模擬真實的 scope 驗證邏輯。

建議：考慮使用更精確的 mock 策略，例如根據輸入的 featureId 和 scope 回傳對應的結果，以確保測試的獨立性和可靠性。

**判斷依據**：測試中使用了 `mockIsFeatureAllowedForScope.mockReturnValue(true)` 和 `mockReturnValue(false)`，但沒有根據輸入參數進行條件回傳，這可能導致測試無法準確驗證 scope 邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:4</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 常數沒有被使用，且註解表明它應該被 lint 工具捕捉。這會增加程式碼噪音，建議移除。

**判斷依據**：diff 中新增了此常數，但後續程式碼並未使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9332 (cache hit 9216) ｜ completion tokens 1286 ｜ PR #14</sub>