<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，讓功能可限定在 org/team/user 層級。主要風險在於 `listFeaturesForUser` 的過濾條件疑似寫反（`!state.globalEnabled`），會回傳全域停用的功能；另外 `setUserFeatureState` 的條件分支邏輯與原本相反，可能造成非 inherit 狀態未寫入。測試中 mock 了 `isFeatureAllowedForScope`，但部分測試未正確驗證 scope 行為。建議先修正這兩個邏輯錯誤，並補齊測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件寫反，回傳全域停用的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件分支邏輯相反，非 inherit 狀態不會寫入 | 0.90 |
| ⚠️ | Major | `packages/features/feature-opt-in/config.ts:4` | [R06] 未使用的常數 UNUSED_CONSTANT 會觸發 lint 警告 | 0.85 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.test.ts:10` | 測試中 mock 的 isFeatureAllowedForScope 可能導致測試無法驗證真實邏輯 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試中 mock isFeatureAllowedForScope 可能隱藏 scope 相關的整合問題 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件寫反，回傳全域停用的功能</summary>

在 `listFeaturesForUser` 中，原本的過濾條件是 `filter((state) => state.globalEnabled)`，但此 PR 改成了 `filter((state) => !state.globalEnabled)`。這會導致只回傳全域停用的功能，而全域啟用的功能反而被排除。這會讓使用者看不到應該可用的功能，嚴重影響功能開關的正確性。

建議改回 `filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中此行由 `filter((state) => state.globalEnabled)` 改為 `filter((state) => !state.globalEnabled)`，且註解仍寫「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」，明顯矛盾。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件分支邏輯相反，非 inherit 狀態不會寫入</summary>

原本的邏輯是 `if (state === "inherit")` 執行 inherit 分支，否則執行 enabled/disabled 分支。此 PR 改成 `if (state !== "inherit")`，導致 enabled/disabled 狀態會進入原本 inherit 的 else 分支，而 inherit 狀態反而進入 enabled/disabled 分支。這會造成狀態設定完全錯誤。

建議改回 `if (state === "inherit")`。

**判斷依據**：diff 顯示原本的 `if (state === "inherit")` 被改為 `if (state !== "inherit")`，且後續分支內容未變，邏輯顛倒。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/config.ts:4</code> [R06] 未使用的常數 UNUSED_CONSTANT 會觸發 lint 警告</summary>

新增的 `const UNUSED_CONSTANT = "this-should-be-removed";` 沒有被使用，且註解寫明「Unused import that should be caught by linting」。這會違反 R06（lint 警告視為錯誤），導致 CI 失敗。

建議移除該常數。

**判斷依據**：diff 新增了未使用的常數，且註解表明這是故意留下的 lint 錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.test.ts:10</code> 測試中 mock 的 isFeatureAllowedForScope 可能導致測試無法驗證真實邏輯</summary>

在 `FeatureOptInService.test.ts` 中，`vi.mock("../config", ...)` 將 `isFeatureAllowedForScope` 替換為 `mockIsFeatureAllowedForScope`，並在 `beforeEach` 中設定為回傳 `true`。這使得所有測試都假設功能允許，無法驗證 scope 限制的實際行為。雖然有測試手動設定回傳 `false`，但整體測試覆蓋可能不足。

建議增加更多測試案例，直接使用真實的 config 或更精確的 mock，以驗證 scope 過濾邏輯。

**判斷依據**：測試檔案中 mock 了 `isFeatureAllowedForScope`，且預設回傳 `true`，可能掩蓋真實的 scope 驗證錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試中 mock isFeatureAllowedForScope 可能隱藏 scope 相關的整合問題</summary>

在整合測試中，`vi.mock("../config", ...)` 將 `isFeatureAllowedForScope` 替換為永遠回傳 `true` 的函式。這表示整合測試不會驗證 scope 限制在實際資料庫操作中的行為。雖然整合測試的重點是資料庫行為，但 scope 驗證是服務層的重要邏輯，應該在整合測試中保留真實實作，或至少增加針對 scope 的整合測試。

建議移除這個 mock，或增加測試案例來驗證 scope 限制在整合環境下的正確性。

**判斷依據**：整合測試中 mock 了 `isFeatureAllowedForScope`，使其永遠回傳 `true`，可能導致 scope 驗證邏輯未在整合測試中覆蓋。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10797 (cache hit 9344) ｜ completion tokens 1570 ｜ PR #14</sub>