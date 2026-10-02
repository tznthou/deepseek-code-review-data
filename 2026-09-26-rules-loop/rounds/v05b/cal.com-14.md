<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，讓功能可限定在 org/team/user 層級。主要風險在於 `listFeaturesForUser` 的過濾條件被反轉（`!state.globalEnabled`），會回傳未啟用的功能；另外 `setUserFeatureState` 的條件判斷從 `state === "inherit"` 改成 `state !== "inherit"`，導致 enabled/disabled 狀態走錯分支。測試中 mock 了 `isFeatureAllowedForScope`，可能掩蓋實際整合問題。建議先修正這兩個邏輯錯誤，並移除未使用的常數。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件反轉，回傳未啟用的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件判斷錯誤，enabled/disabled 走錯分支 | 0.90 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試 mock 掉 isFeatureAllowedForScope，可能掩蓋實際問題 | 0.70 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:5` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件反轉，回傳未啟用的功能</summary>

原本的程式碼是 `.filter((state) => state.globalEnabled)`，但這次修改變成 `.filter((state) => !state.globalEnabled)`。這會讓使用者看到所有「全域未啟用」的功能，而看不到已啟用的功能，完全違反預期行為。

**失敗情境**：當某功能在全域設定為啟用時，使用者呼叫 `listFeaturesForUser` 將不會看到該功能；反之，未啟用的功能卻會出現在列表中。

**建議修法**：改回 `.filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，邏輯相反。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件判斷錯誤，enabled/disabled 走錯分支</summary>

原本的條件是 `if (state === "inherit")`，但修改後變成 `if (state !== "inherit")`。這會導致當 state 為 "enabled" 或 "disabled" 時，程式碼進入原本處理 "inherit" 的分支，而 "inherit" 狀態反而進入另一個分支。

**失敗情境**：使用者嘗試設定功能為 enabled 時，會執行到 `const { assignedBy } = input;` 並呼叫 `setUserFeatureState`，但傳入的 assignedBy 可能不存在，造成執行時期錯誤。

**建議修法**：改回 `if (state === "inherit")`。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試 mock 掉 isFeatureAllowedForScope，可能掩蓋實際問題</summary>

在整合測試中，`isFeatureAllowedForScope` 被 mock 成永遠回傳 `true`。這使得整合測試無法驗證 scope 驗證邏輯與資料庫互動的正確性。雖然單元測試有覆蓋該函式，但整合測試應該使用真實的 config 來確保整體行為正確。

**建議修法**：移除這個 mock，讓整合測試使用實際的 `isFeatureAllowedForScope` 實作。

**判斷依據**：diff 新增此 mock，且註解說明是為了讓整合測試專注於資料庫行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:5</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 常數沒有被任何地方使用，且註解也說明它應該被 lint 移除。這會觸發 lint 警告，違反 [R06] 的規範。

**建議修法**：直接刪除此常數。

**判斷依據**：diff 新增此行，且無其他引用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10776 (cache hit 10752) ｜ completion tokens 1209 ｜ PR #14</sub>