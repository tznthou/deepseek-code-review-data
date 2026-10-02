<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 的搜尋狀態從可選的 atom 切換為一律使用 URL query，並移除了相關的 hydration 元件。主要風險在於 `useMarketplaceSearchMode` 中條件判斷的邏輯反轉，可能導致搜尋模式判斷錯誤；此外 `usePluginPageContext` 的型別從函式放寬為 any，降低型別安全。建議修正邏輯並恢復型別。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 搜尋模式判斷邏輯反轉 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | usePluginPageContext 的 selector 參數型別從函式放寬為 any | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 搜尋模式判斷邏輯反轉</summary>

在 `useMarketplaceSearchMode` 中，原本的條件 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 被改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了否定運算子。這會導致當 `activePluginType` 屬於有 collections 的類別時，`isSearchMode` 會被錯誤地設為 true，反之亦然。例如，若使用者選擇的類別是 'all'（假設不在集合中），原本應為非搜尋模式，現在卻會進入搜尋模式，影響 UI 顯示與資料擷取邏輯。

**判斷依據**：diff 中此行由 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了 `!`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> usePluginPageContext 的 selector 參數型別從函式放寬為 any</summary>

原本 `selector` 的型別是 `(value: PluginPageContextValue) => any`，現在改為 `any`。這會失去型別檢查，允許傳入非函式值，可能導致執行時期錯誤（例如 `useContextSelector` 內部呼叫 selector 時拋出 TypeError）。建議恢復原本的函式型別，或使用更精確的泛型。

**判斷依據**：diff 中此行由 `selector: (value: PluginPageContextValue) => any` 改為 `selector: any`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3136 (cache hit 3072) ｜ completion tokens 654 ｜ PR #9</sub>