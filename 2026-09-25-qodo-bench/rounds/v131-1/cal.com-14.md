<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 功能新增了 scope 設定（org/team/user），並在服務層加入對應的驗證邏輯。主要風險在於 `listFeaturesForUser` 的過濾條件被反轉（`!state.globalEnabled`），可能導致回傳未啟用的功能；此外，`setUserFeatureState` 的條件判斷從 `state === "inherit"` 改為 `state !== "inherit"`，可能造成非 inherit 狀態的 assignedBy 處理錯誤。另有未使用的常數與測試中 mock 行為可能掩蓋實際問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件反轉，回傳未啟用的功能 | 0.95 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件判斷反轉，可能導致 assignedBy 處理錯誤 | 0.85 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:5` | 未使用的常數 UNUSED_CONSTANT | 0.90 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試 mock isFeatureAllowedForScope 可能掩蓋實際問題 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件反轉，回傳未啟用的功能</summary>

在 `listFeaturesForUser` 中，原本的 `.filter((state) => state.globalEnabled)` 被改為 `.filter((state) => !state.globalEnabled)`，這會導致只回傳 `globalEnabled` 為 false 的功能，與方法註解「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」矛盾。這將使前端無法取得任何已啟用的功能，造成功能失效。

**建議修法**：將條件改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且方法註解明確指出應回傳 globally enabled 的功能。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件判斷反轉，可能導致 assignedBy 處理錯誤</summary>

原本的 `if (state === "inherit")` 被改為 `if (state !== "inherit")`，這使得當 state 為 "enabled" 或 "disabled" 時，會進入原本處理 inherit 的分支，嘗試從 input 中取得 `assignedBy` 並呼叫 `setUserFeatureState`。但 TypeScript 的 union type 保證在 state 非 inherit 時 input 一定包含 `assignedBy`，因此不會有 runtime error，但邏輯上與原本意圖相反。

**建議修法**：改回 `if (state === "inherit")`。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，且後續的 else 分支處理 inherit 狀態。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:5</code> 未使用的常數 UNUSED_CONSTANT</summary>

新增的 `UNUSED_CONSTANT` 常數未被使用，且其值為字串，可能觸發 lint 規則（如 no-unused-vars）。建議移除。

**判斷依據**：diff 中新增此行，且後續程式碼未引用此常數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試 mock isFeatureAllowedForScope 可能掩蓋實際問題</summary>

在整合測試中，`isFeatureAllowedForScope` 被 mock 為永遠回傳 true，這可能導致測試無法涵蓋 scope 驗證的整合行為。雖然單元測試有覆蓋驗證邏輯，但整合測試應確保實際的 config 與服務層互動正確。建議考慮使用真實的 config 或至少驗證 mock 的呼叫次數。

**判斷依據**：diff 中新增此 mock，且未在其他測試中驗證 isFeatureAllowedForScope 的呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9332 (cache hit 1408) ｜ completion tokens 1164 ｜ PR #14</sub>