<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定，讓功能可依 org/team/user 層級啟用。主要風險在於 `listFeaturesForUser` 的過濾條件疑似寫反（應回傳 globalEnabled 為 true 的功能，但程式碼卻回傳 false），以及 `setUserFeatureState` 的條件分支邏輯顛倒（應在 state 為 inherit 時直接設定，但程式碼卻在非 inherit 時直接設定）。此外，config.ts 中新增了未使用的常數，且測試中 mock 了 `isFeatureAllowedForScope` 可能掩蓋整合問題。建議優先修正這兩個邏輯錯誤，並移除未使用的程式碼。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件寫反：回傳 globalEnabled 為 false 的功能 | 0.95 |
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 條件分支邏輯顛倒：inherit 時未直接設定 | 0.90 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試中 mock isFeatureAllowedForScope 可能掩蓋 scope 驗證問題 | 0.75 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 回傳型別可能包含 undefined | 0.70 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:4` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件寫反：回傳 globalEnabled 為 false 的功能</summary>

在 `listFeaturesForUser` 中，原本的過濾條件是 `.filter((state) => state.globalEnabled)`，但此 PR 改成了 `.filter((state) => !state.globalEnabled)`。這會導致只回傳全域停用的功能，而全域啟用的功能反而被排除。這與方法註解「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」矛盾，且會讓使用者看不到應該可用的功能。

**失敗情境**：當某功能在 flags 中設定為 enabled 時，使用者呼叫 `listFeaturesForUser` 將不會看到該功能，造成功能無法被使用者啟用。

**建議修法**：將條件改回 `.filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且方法註解仍寫著「globally enabled」

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 條件分支邏輯顛倒：inherit 時未直接設定</summary>

在 `setUserFeatureState` 中，原本的邏輯是 `if (state === "inherit") { 直接設定 } else { 處理 assignedBy }`，但此 PR 改成了 `if (state !== "inherit") { 直接設定 } else { 處理 assignedBy }`。這會導致當 state 為 "inherit" 時，程式碼進入 else 分支，嘗試從 input 取得 `assignedBy`，但該屬性在 inherit 的型別中並不存在，可能導致執行時錯誤或型別不符。

**失敗情境**：當使用者呼叫 `setUserFeatureState` 並傳入 `state: "inherit"` 時，程式碼會執行 `const { assignedBy } = input;`，但 input 的型別為 `{ userId: number; featureId: FeatureId; state: "inherit" }`，沒有 `assignedBy` 屬性，因此 `assignedBy` 會是 `undefined`，後續可能拋出錯誤或產生不正確的行為。

**建議修法**：將條件改回 `if (state === "inherit") { 直接設定 } else { 處理 assignedBy }`。

**判斷依據**：diff 中條件由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，且後續 else 分支使用了 `assignedBy`

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試中 mock isFeatureAllowedForScope 可能掩蓋 scope 驗證問題</summary>

在整合測試中，使用 `vi.mock` 將 `isFeatureAllowedForScope` 替換為永遠回傳 true 的函式。這會使得整合測試無法驗證 scope 驗證邏輯是否正確運作，可能導致實際部署時 scope 驗證失效而未被發現。

**失敗情境**：如果 `isFeatureAllowedForScope` 的實作有誤（例如判斷條件錯誤），整合測試仍會通過，因為 mock 永遠回傳 true，使得錯誤被掩蓋。

**建議修法**：在整合測試中不要 mock `isFeatureAllowedForScope`，或者使用真實的實作來驗證 scope 驗證。如果必須 mock，應在測試中明確驗證該函式被呼叫且參數正確。

**判斷依據**：diff 中新增了此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior.」

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 回傳型別可能包含 undefined</summary>

在 `listFeaturesForUser` 中，`featureIds.map((featureId) => resolvedStates[featureId])` 的結果可能包含 `undefined`，因為 `resolvedStates` 可能不包含所有 featureId 的鍵。後續的 `.filter((state) => !state.globalEnabled)` 在 state 為 undefined 時會拋出錯誤。

**失敗情境**：如果 `resolveFeatureStatesAcrossTeams` 沒有為某個 featureId 回傳狀態（例如該功能在資料庫中不存在），則 `resolvedStates[featureId]` 會是 undefined，導致 `.filter` 中的 `state.globalEnabled` 拋出 TypeError。

**建議修法**：在 map 後先過濾掉 undefined，或確保 `resolveFeatureStatesAcrossTeams` 一定回傳所有 featureId 的狀態。

**判斷依據**：此行程式碼直接對 map 結果呼叫 filter，未處理可能的 undefined

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:4</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

在 `config.ts` 中新增了 `const UNUSED_CONSTANT = "this-should-be-removed";`，但此常數未被使用。這會觸發 lint 警告（未使用的變數），且違反程式碼整潔原則。

**建議修法**：移除該常數。

**判斷依據**：diff 中新增了此常數，且未在其他地方使用

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10817 (cache hit 10752) ｜ completion tokens 1879 ｜ PR #14</sub>