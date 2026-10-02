<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，區分 org、team、user 三種層級，並在服務層加入驗證。主要風險在於 `listFeaturesForUser` 的過濾條件疑似寫反（應回傳 globalEnabled 為 true 的項目，但程式碼改為回傳 false），以及 `setUserFeatureState` 的條件判斷邏輯反轉（原本 state === 'inherit' 才呼叫 repository，現在變成 state !== 'inherit' 才呼叫，導致 enabled/disabled 狀態不會被寫入）。此外，config.ts 中新增了未使用的常數，且測試中 mock 了 `isFeatureAllowedForScope` 使其永遠回傳 true，可能掩蓋整合測試中的 scope 驗證問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件寫反，導致回傳 globalEnabled 為 false 的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件判斷反轉，導致 enabled/disabled 狀態不會被寫入 | 0.95 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試中 mock isFeatureAllowedForScope 永遠回傳 true，可能掩蓋 scope 驗證問題 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:4` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件寫反，導致回傳 globalEnabled 為 false 的功能</summary>

原本的程式碼是 `.filter((state) => state.globalEnabled)`，但此 PR 改成了 `.filter((state) => !state.globalEnabled)`。這會讓使用者看不到任何全域啟用的功能，反而看到被停用的功能。

**失敗情境**：當某個功能在 flags 設定中 `enabled: true` 時，使用者呼叫 `listFeaturesForUser` 將不會看到該功能；反之，若功能被停用，卻會出現在回傳結果中。

**建議修法**：改回 `.filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中將原本的 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且註解仍寫著「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」，明顯矛盾。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件判斷反轉，導致 enabled/disabled 狀態不會被寫入</summary>

原本的邏輯是 `if (state === "inherit")` 才呼叫 `setUserFeatureState`，否則走 `assignedBy` 分支。但此 PR 將條件改為 `if (state !== "inherit")`，使得當 state 為 `enabled` 或 `disabled` 時，會進入原本處理 `inherit` 的 else 分支，而該分支會嘗試從 input 取得 `assignedBy`，但 input 型別中 `assignedBy` 是必要的，因此可能不會立即出錯，但邏輯完全相反。

**失敗情境**：使用者嘗試將功能設為 enabled 或 disabled 時，實際呼叫的是 `setUserFeatureState({ userId, featureId, state })`，但這個呼叫缺少 `assignedBy`，可能導致 repository 層錯誤或資料不一致。

**建議修法**：改回 `if (state === "inherit")`。

**判斷依據**：diff 中將 `if (state === "inherit")` 改為 `if (state !== "inherit")`，但後續的 else 分支仍假設 state 為 inherit 且需要 assignedBy。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試中 mock isFeatureAllowedForScope 永遠回傳 true，可能掩蓋 scope 驗證問題</summary>

在整合測試中，`vi.mock` 將 `isFeatureAllowedForScope` 替換為永遠回傳 true 的函式。這表示整合測試不會驗證 scope 驗證邏輯，即使服務層的 scope 驗證有 bug，整合測試仍會通過。

**失敗情境**：如果未來有人誤改 `isFeatureAllowedForScope` 或服務層的呼叫方式，整合測試無法捕捉到 scope 驗證失效的問題。

**建議修法**：考慮在整合測試中保留真實的 `isFeatureAllowedForScope`，或至少加入一個測試案例驗證 scope 驗證在整合環境中確實被執行。

**判斷依據**：diff 中新增了此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior」，但這可能導致整合測試無法涵蓋完整的服務行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:4</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 沒有被任何地方使用，且註解也說「Unused import that should be caught by linting」。這會觸發 lint 錯誤，並增加程式碼噪音。

**建議修法**：直接刪除此常數。

**判斷依據**：diff 中新增了此常數，且沒有其他程式碼引用它。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9368 (cache hit 9344) ｜ completion tokens 1486 ｜ PR #14</sub>