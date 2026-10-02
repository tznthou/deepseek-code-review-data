<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 功能新增了 scope 設定，讓功能可以分別在 org、team、user 層級啟用。主要變更包括新增 scope 型別與相關輔助函式、修改服務層以進行 scope 驗證、更新 tRPC 路由傳入 scope，以及調整 UI 顯示條件。整體方向合理，但存在一個明確的邏輯錯誤（listFeaturesForUser 的 filter 條件反轉），可能導致使用者看不到任何功能；此外，config.ts 中有一個未使用的常數，違反 lint 規範。建議先修正這兩個問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 的 filter 條件反轉，導致只回傳全域停用的功能 | 0.95 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:4` | [R06] 未使用的常數 UNUSED_CONSTANT 會觸發 lint 警告 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 的 filter 條件反轉，導致只回傳全域停用的功能</summary>

在 `listFeaturesForUser` 中，原本的 `.filter((state) => state.globalEnabled)` 被改成了 `.filter((state) => !state.globalEnabled)`。這會讓使用者只看到全域停用的功能，而看不到全域啟用的功能，完全違背預期行為。

**失敗情境**：當某個功能在 flags 設定中為啟用（globalEnabled = true）時，它會被過濾掉，使用者無法在設定頁看到或管理該功能。

**建議修法**：改回 `.filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中此行由 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且前後文未顯示任何意圖變更此行為的註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:4</code> [R06] 未使用的常數 UNUSED_CONSTANT 會觸發 lint 警告</summary>

新增的 `const UNUSED_CONSTANT = "this-should-be-removed";` 從未被使用。根據規範 R06，pre-commit hook 會以 `--error-on-warnings` 執行 Biome lint，未使用的變數會導致 lint 失敗，阻擋 commit。

**建議修法**：移除此常數。

**判斷依據**：diff 中新增了此常數，且後續程式碼未引用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10807 (cache hit 9344) ｜ completion tokens 695 ｜ PR #14</sub>