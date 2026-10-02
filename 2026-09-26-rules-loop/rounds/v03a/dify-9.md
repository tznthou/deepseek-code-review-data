<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 搜尋狀態從可選的 URL 保留改為一律保留在 URL 中，並移除了相關的 atom 與 hydration 元件。主要風險在於 `useMarketplaceSearchMode` 中布林邏輯的變更可能導致搜尋模式判斷錯誤，以及 `usePluginPageContext` 的參數型別從具體函式放寬為 `any`，違反專案規範 R09。建議修正邏輯並恢復型別安全。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 布林邏輯反轉可能導致搜尋模式判斷錯誤 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] 使用 any 型別違反 TypeScript 型別安全規範 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 布林邏輯反轉可能導致搜尋模式判斷錯誤</summary>

在 `useMarketplaceSearchMode` 中，原本的 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 被改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了否定運算子。這會反轉條件：原本當 activePluginType 不屬於特定集合時會進入搜尋模式，現在變成屬於集合時才進入。若此邏輯用於判斷是否顯示搜尋結果或切換 UI，將導致行為完全相反。請確認此變更是否為預期，若非預期請恢復原邏輯。

**判斷依據**：diff 中此行由 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] 使用 any 型別違反 TypeScript 型別安全規範</summary>

`usePluginPageContext` 的參數 `selector` 型別從具體的函式型別改為 `any`，這會繞過 TypeScript 的型別檢查，可能導致執行時期錯誤。專案規範 R09 明確禁止使用 `any`。請恢復原本的具體型別，或使用 `unknown` 配合型別守衛。

**判斷依據**：diff 中此行由 `selector: (value: PluginPageContextValue) => any` 改為 `selector: any`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5861 (cache hit 3072) ｜ completion tokens 654 ｜ PR #9</sub>