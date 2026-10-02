<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 的搜尋狀態從可選的 atom 儲存改為一律使用 URL query 參數，並刪除了相關的 hydration 元件。主要風險在於 `useMarketplaceSearchMode` 中布林邏輯的變更可能導致搜尋模式判斷錯誤，以及 `usePluginPageContext` 的 selector 參數型別從函式放寬為 `any`，違反專案規範 R09。建議先修正這兩個問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 布林邏輯變更可能導致搜尋模式判斷錯誤 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] 使用 any 型別違反 TypeScript 規範 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 布林邏輯變更可能導致搜尋模式判斷錯誤</summary>

原本的條件是 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，表示當 activePluginType 不在集合中時為 true；修改後變成 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，邏輯完全相反。這會導致當 activePluginType 屬於集合時，即使沒有搜尋文字或標籤，也會被誤判為搜尋模式。

**失敗情境**：使用者選擇一個有 collections 的 plugin 類別（例如某個特定類別），且沒有輸入任何搜尋文字或選擇標籤，此時 `isSearchMode` 會錯誤地回傳 `true`，可能導致 UI 顯示搜尋結果而非一般列表。

**建議修法**：將條件改回 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，或確認此變更是否為預期行為。

**判斷依據**：diff 中此行將原本的 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了邏輯 NOT 運算子。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] 使用 any 型別違反 TypeScript 規範</summary>

`usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這完全失去了型別檢查，違反專案規範 R09（TypeScript Must Avoid any Type Annotations）。

**失敗情境**：呼叫端傳入錯誤的 selector（例如非函式或回傳型別不符）時，TypeScript 不會報錯，可能導致執行時期錯誤。

**建議修法**：保留原本的函式型別，或使用更精確的泛型型別，例如 `selector: (value: PluginPageContextValue) => unknown` 或 `selector: (value: PluginPageContextValue) => T`。

**判斷依據**：diff 中此行將 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5861 (cache hit 5760) ｜ completion tokens 816 ｜ PR #9</sub>