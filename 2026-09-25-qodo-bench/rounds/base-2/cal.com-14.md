<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 加入 scope 設定（org/team/user），並在 service 層加入 scope 驗證。主要風險在於 `listFeaturesForUser` 的過濾條件疑似寫反（應回傳 globalEnabled 為 true 的項目，但現在回傳 false 的），以及 config.ts 中殘留未使用的常數。此外，測試中 mock 了 `isFeatureAllowedForScope`，可能使整合測試無法真正驗證 scope 邏輯。整體方向合理，但需修正上述問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件寫反，導致回傳 globalEnabled 為 false 的功能 | 0.95 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13` | 整合測試 mock 掉 isFeatureAllowedForScope，可能無法驗證 scope 邏輯 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:4` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件寫反，導致回傳 globalEnabled 為 false 的功能</summary>

在 `listFeaturesForUser` 中，原本的過濾條件是 `.filter((state) => state.globalEnabled)`，但此 PR 改成了 `.filter((state) => !state.globalEnabled)`。這會讓使用者看不到任何全域啟用的功能，反而看到被停用的功能，完全違反預期行為。

**失敗情境**：當某功能在 flags 中 `enabled: true` 時，使用者呼叫 `listFeaturesForUser` 將不會看到該功能；反之，若 `enabled: false`，反而會出現在列表中。

**建議**：改回 `.filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且註解仍寫著「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」，明顯矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:13</code> 整合測試 mock 掉 isFeatureAllowedForScope，可能無法驗證 scope 邏輯</summary>

在整合測試中，`isFeatureAllowedForScope` 被 mock 成永遠回傳 `true`。這使得整合測試無法驗證 service 層的 scope 驗證是否正確運作，可能讓錯誤的 scope 邏輯通過測試。

**失敗情境**：若 `isFeatureAllowedForScope` 的實作有誤（例如判斷條件寫反），整合測試仍會通過，因為 mock 繞過了實際邏輯。

**建議**：考慮在整合測試中使用真實的 `isFeatureAllowedForScope`，或至少加入一個測試案例來驗證 scope 驗證在整合情境下的行為。

**判斷依據**：diff 中新增了此 mock，且註解說明「The scope validation logic is tested in unit tests; integration tests focus on database behavior.」但這可能降低整合測試的覆蓋率。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:4</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 常數未被使用，且註解也表明這是應該被 lint 抓到的。這會造成程式碼雜訊，並可能讓 CI 的 lint 檢查失敗。

**建議**：移除該常數及其註解。

**判斷依據**：diff 中新增了此常數，且沒有其他程式碼引用它。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9368 (cache hit 9344) ｜ completion tokens 1032 ｜ PR #14</sub>