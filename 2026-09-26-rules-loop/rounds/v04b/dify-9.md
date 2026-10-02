<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 移除了 marketplace 搜尋狀態的條件式保留機制，改為一律將搜尋文字、分類與標籤同步到 URL query string。主要風險在於 `useMarketplaceSearchMode` 中對 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 的邏輯反轉，可能導致搜尋模式判斷錯誤；此外 `usePluginPageContext` 的 selector 參數型別從函式改為 `any`，違反專案規範 R09，且會喪失型別安全。建議先修正這兩個問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 搜尋模式判斷邏輯反轉 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] 使用 any 型別作為 selector 參數 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 搜尋模式判斷邏輯反轉</summary>

原本的條件是 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，表示當分類不屬於「有 collections 的分類」時視為搜尋模式。修改後變成 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，邏輯完全相反。

這會導致：當使用者選擇的分類屬於 `PLUGIN_CATEGORY_WITH_COLLECTIONS`（例如某個有 collections 的分類）時，即使沒有輸入任何搜尋文字或標籤，`isSearchMode` 也會被設為 `true`，進而可能顯示錯誤的 UI 或觸發不必要的搜尋行為。

建議改回原本的否定邏輯，或確認此變更是否為刻意行為並加上對應的測試。

**判斷依據**：diff 中此行由 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了否定運算子。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] 使用 any 型別作為 selector 參數</summary>

`usePluginPageContext` 的 selector 參數型別從原本的函式型別改為 `any`，這違反了專案規範 R09（TypeScript Must Avoid any Type Annotations）。

使用 `any` 會讓 TypeScript 無法檢查傳入的 selector 是否符合 `useContextSelector` 的預期，可能導致執行時期錯誤。

建議保留原本的函式型別，或使用更精確的泛型型別，例如 `(value: PluginPageContextValue) => unknown` 或 `(value: PluginPageContextValue) => any`（若有必要），但避免直接使用 `any` 作為參數型別。

**判斷依據**：diff 中此行由 `selector: (value: PluginPageContextValue) => any` 改為 `selector: any`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4412 (cache hit 4352) ｜ completion tokens 789 ｜ PR #9</sub>