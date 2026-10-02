<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，並在 service 層加入 scope 驗證。主要風險在於 `listFeaturesForUser` 的 filter 條件疑似寫反，導致只回傳全域停用的功能；此外，`setUserFeatureState` 的條件判斷也疑似顛倒，可能造成非 inherit 狀態時走錯分支。另有未使用的常數與測試中 mock 可能掩蓋真實驗證邏輯等問題。建議先修正這兩個邏輯錯誤再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 的 filter 條件寫反，只回傳全域停用的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 的條件判斷寫反，非 inherit 狀態會走錯分支 | 0.90 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試中 mock 掉 isFeatureAllowedForScope，可能掩蓋真實驗證邏輯 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:5` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.90 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.test.ts:22` | 測試中的 mock 可能與實際 config 行為不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 的 filter 條件寫反，只回傳全域停用的功能</summary>

原本的程式碼是 `.filter((state) => state.globalEnabled)`，但這次修改後變成 `.filter((state) => !state.globalEnabled)`。這會導致 `listFeaturesForUser` 只回傳 `globalEnabled` 為 `false` 的功能，與 JSDoc 中「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」的描述完全相反。

**失敗情境**：當使用者呼叫此方法時，所有全域啟用的功能都會被過濾掉，只留下全域停用的功能，造成前端顯示錯誤或功能無法使用。

**建議**：將條件改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且 JSDoc 仍宣稱只回傳 globally enabled 的功能。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 的條件判斷寫反，非 inherit 狀態會走錯分支</summary>

原本的程式碼是 `if (state === "inherit")`，但這次修改後變成 `if (state !== "inherit")`。這會導致當 `state` 為 `"enabled"` 或 `"disabled"` 時，進入原本處理 `inherit` 的分支（呼叫 `setUserFeatureState` 時沒有 `assignedBy`），而當 `state` 為 `"inherit"` 時，反而進入原本處理 `enabled/disabled` 的分支（需要 `assignedBy`）。

**失敗情境**：
- 當使用者設定 `state: "enabled"` 且提供 `assignedBy` 時，程式會嘗試呼叫 `this.featuresRepository.setUserFeatureState({ userId, featureId, state })`，但 repository 的實作可能預期有 `assignedBy`，導致型別錯誤或執行時期錯誤。
- 當使用者設定 `state: "inherit"` 時，程式會進入 `else` 分支，嘗試從 `input` 取得 `assignedBy`，但 `input` 的型別是 `{ userId: number; featureId: FeatureId; state: "inherit" }`，根本沒有 `assignedBy` 屬性，會導致 `assignedBy` 為 `undefined`，進而可能產生錯誤。

**建議**：將條件改回 `if (state === "inherit")`。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，且後續分支邏輯未同步調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試中 mock 掉 isFeatureAllowedForScope，可能掩蓋真實驗證邏輯</summary>

在整合測試中，`vi.mock("../config", ...)` 將 `isFeatureAllowedForScope` 替換為永遠回傳 `true` 的函式。這表示整合測試不會驗證 scope 驗證邏輯，即使 service 中的 scope 驗證有誤，整合測試仍會通過。

**失敗情境**：如果 `isFeatureAllowedForScope` 的實作有 bug（例如判斷條件錯誤），整合測試無法發現，因為它被 mock 掉了。

**建議**：整合測試應使用真實的 `isFeatureAllowedForScope`，或至少使用一個能反映真實邏輯的 mock。如果整合測試的目的是專注於資料庫行為，可以考慮將 scope 驗證的測試完全放在單元測試中，但整合測試不應完全繞過驗證。

**判斷依據**：diff 中新增了此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior.」

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:5</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 常數沒有被任何地方使用，且其名稱暗示這是故意留下的未使用程式碼。這會觸發 lint 警告（例如 no-unused-vars），並增加不必要的維護負擔。

**建議**：移除該常數。

**判斷依據**：diff 中新增了此常數，且後續程式碼未引用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.test.ts:22</code> 測試中的 mock 可能與實際 config 行為不一致</summary>

在單元測試中，`vi.mock("../config", ...)` 回傳的 `getOptInFeaturesForScope` 永遠回傳完整的 `mockFeatures` 陣列，沒有根據 scope 過濾。這可能導致測試無法驗證 `getOptInFeaturesForScope` 的實際過濾邏輯，且如果 service 依賴此函式的過濾結果，測試可能無法捕捉到相關錯誤。

**建議**：讓 mock 的 `getOptInFeaturesForScope` 根據傳入的 scope 回傳對應的功能，或使用真實的 config 函式。

**判斷依據**：diff 中新增了此 mock 回傳值，且未根據 scope 參數過濾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9992 (cache hit 9344) ｜ completion tokens 1804 ｜ PR #14</sub>