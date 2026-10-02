<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 功能新增了 scope 設定，允許功能在 org、team、user 三個層級分別啟用。主要變更包括：在 config 中新增 scope 欄位與相關輔助函式、在 service 層加入 scope 驗證、更新 tRPC router 傳遞 scope、以及調整 UI 使用新的常數。整體方向合理，但存在一個明確的邏輯錯誤（listFeaturesForUser 的 filter 條件反轉）會導致使用者看不到任何功能，必須修正。此外，測試中 mock 了 isFeatureAllowedForScope 導致整合測試失去驗證效果，且新增的 UNUSED_CONSTANT 違反 lint 規範。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 的 filter 條件反轉，導致回傳空陣列 | 0.99 |
| ⚠️ | Major | `packages/features/feature-opt-in/config.ts:4` | [R06] 新增未使用的常數 UNUSED_CONSTANT，將觸發 lint 錯誤 | 0.95 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試中 mock 掉 isFeatureAllowedForScope，使 scope 驗證未被測試 | 0.90 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.ts:264` | setUserFeatureState 中 state 判斷邏輯反轉，可能導致行為錯誤 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.ts:288` | setTeamFeatureState 中 scope 預設值可能導致 org 操作被誤判為 team | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 的 filter 條件反轉，導致回傳空陣列</summary>

在 `listFeaturesForUser` 中，原本的 `.filter((state) => state.globalEnabled)` 被改成了 `.filter((state) => !state.globalEnabled)`，這會讓所有全域啟用的功能都被過濾掉，只回傳全域停用的功能。這會導致使用者介面上看不到任何可用的 opt-in 功能。

**失敗情境**：當 `OPT_IN_FEATURES` 中有任何 `globalEnabled` 為 true 的功能時，呼叫 `listFeaturesForUser` 會回傳空陣列，使用者無法看到或設定任何功能。

**建議修法**：將條件改回 `state.globalEnabled`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，邏輯明顯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/config.ts:4</code> [R06] 新增未使用的常數 UNUSED_CONSTANT，將觸發 lint 錯誤</summary>

在 `config.ts` 中新增了 `const UNUSED_CONSTANT = "this-should-be-removed";`，但此常數從未被使用。根據專案規範 R06，pre-commit hook 會執行 `biome lint --error-on-warnings`，未使用的變數會導致 lint 失敗，阻擋 commit。

**建議修法**：移除該常數。

**判斷依據**：diff 中新增了此常數，且後續程式碼未使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試中 mock 掉 isFeatureAllowedForScope，使 scope 驗證未被測試</summary>

在整合測試中，使用 `vi.mock` 將 `isFeatureAllowedForScope` 替換為永遠回傳 `true` 的函式。這使得整合測試無法驗證 service 層的 scope 驗證邏輯，即使實作有誤，測試仍會通過。

**失敗情境**：若 `setUserFeatureState` 或 `setTeamFeatureState` 中的 scope 驗證邏輯被移除或寫錯，整合測試不會發現。

**建議修法**：不要在整合測試中 mock 此函式，或改為使用真實的 config 資料來測試不同 scope 的行為。

**判斷依據**：diff 中新增了此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior.」

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:264</code> setUserFeatureState 中 state 判斷邏輯反轉，可能導致行為錯誤</summary>

在 `setUserFeatureState` 中，原本的 `if (state === "inherit")` 被改成了 `if (state !== "inherit")`。這會使得當 state 為 "inherit" 時，進入 else 分支執行 `setUserFeatureState`（帶 assignedBy），而當 state 為 "enabled" 或 "disabled" 時，反而執行不帶 assignedBy 的呼叫。這與預期行為相反。

**失敗情境**：當使用者嘗試將功能設為 "inherit" 時，會錯誤地帶入 assignedBy；而設為 "enabled" 或 "disabled" 時，會缺少 assignedBy，可能導致資料庫寫入錯誤或權限檢查失敗。

**建議修法**：將條件改回 `if (state === "inherit")`。

**判斷依據**：diff 中此行由 `if (state === "inherit")` 改為 `if (state !== "inherit")`，且後續分支邏輯未同步調整。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:288</code> setTeamFeatureState 中 scope 預設值可能導致 org 操作被誤判為 team</summary>

在 `setTeamFeatureState` 中，`const scope = input.scope ?? "team";` 將未提供 scope 的呼叫預設為 "team"。然而，在 tRPC router 中，`setForOrganization` 明確傳入 `scope: "org"`，但若未來有其他呼叫未傳 scope 且實際上是 org 操作，可能會被錯誤地以 team scope 驗證。

**失敗情境**：若某個 org 層級的設定操作未傳入 scope，且該功能僅允許 org scope，則會被拒絕；反之，若功能僅允許 team scope，則可能錯誤地允許 org 操作。

**建議修法**：考慮將 scope 設為必填，或根據 teamId 是否為 org ID 來推斷 scope。

**判斷依據**：diff 中新增此行，且 tRPC router 中 `setForOrganization` 有傳入 scope，但其他呼叫可能依賴預設值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10817 (cache hit 9344) ｜ completion tokens 1763 ｜ PR #14</sub>