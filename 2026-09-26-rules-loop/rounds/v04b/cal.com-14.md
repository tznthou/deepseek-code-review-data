<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，允許功能在 org/team/user 層級分別啟用。主要風險在於 `listFeaturesForUser` 的過濾條件被反轉（`!state.globalEnabled`），導致回傳未全域啟用的功能；此外 `setUserFeatureState` 的條件判斷從 `state === "inherit"` 改為 `state !== "inherit"`，可能造成 enabled/disabled 狀態寫入錯誤。另有未使用的常數與測試中 mock 範圍過寬的問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件反轉，回傳未全域啟用的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件判斷反轉，enabled/disabled 狀態可能被誤寫為 inherit | 0.90 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:4` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試中 mock isFeatureAllowedForScope 永遠回傳 true，可能掩蓋 scope 驗證問題 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件反轉，回傳未全域啟用的功能</summary>

在 `listFeaturesForUser` 中，原本應回傳 `globalEnabled` 為 true 的功能，但此處改為 `!state.globalEnabled`，導致回傳所有未全域啟用的功能。這會讓使用者看到不應顯示的功能，且可能造成前端誤判。

建議改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且註解仍寫「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件判斷反轉，enabled/disabled 狀態可能被誤寫為 inherit</summary>

原本邏輯：當 `state === "inherit"` 時執行 inherit 分支，否則執行 enabled/disabled 分支。此處改為 `if (state !== "inherit")`，導致 enabled/disabled 狀態進入 inherit 分支，而 inherit 狀態進入 enabled/disabled 分支。這會造成使用者設定功能時寫入錯誤的狀態。

建議改回 `if (state === "inherit")`。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，且後續分支邏輯未變。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:4</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 常數未被使用，且註解表明這是故意留下的。這會觸發 lint 警告（若 CI 有設定），也增加程式碼噪音。建議移除。

**判斷依據**：diff 中新增此常數，且未在其他地方使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試中 mock isFeatureAllowedForScope 永遠回傳 true，可能掩蓋 scope 驗證問題</summary>

在整合測試中，`isFeatureAllowedForScope` 被 mock 為永遠回傳 true，這使得整合測試無法驗證 scope 驗證邏輯是否正確。雖然單元測試有覆蓋，但整合測試應盡量貼近真實行為。建議考慮使用實際的 config 或更精確的 mock。

**判斷依據**：diff 中新增此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9992 (cache hit 9984) ｜ completion tokens 1131 ｜ PR #14</sub>