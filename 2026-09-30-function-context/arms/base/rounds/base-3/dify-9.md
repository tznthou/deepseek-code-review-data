<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 的搜尋狀態從可選的 atom 切換為一律使用 URL query，並移除了相關的 hydration 元件與 atom。主要風險在於 `useMarketplaceSearchMode` 中布林邏輯的變更（移除 `!`）可能導致搜尋模式判斷錯誤，以及 `usePluginPageContext` 的 selector 型別從函式放寬為 `any`，喪失型別安全。建議優先修正這兩個問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 布林邏輯變更可能導致搜尋模式判斷錯誤 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | selector 參數型別從函式放寬為 any，喪失型別安全 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 布林邏輯變更可能導致搜尋模式判斷錯誤</summary>

在 `useMarketplaceSearchMode` 中，原本的條件是 `(searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，現在改為 `(searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!` 運算子。這會反轉當 `searchMode` 為 null/undefined 時的預設行為：原本當 activePluginType 不在集合中時會進入搜尋模式，現在變成在集合中時才進入搜尋模式。這可能導致在非集合分類下無法正確顯示搜尋模式，或在集合分類下錯誤顯示搜尋模式。請確認此變更是否為預期行為，若非預期請恢復 `!`。

**判斷依據**：diff 中此行由 `|| (searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))` 改為 `|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> selector 參數型別從函式放寬為 any，喪失型別安全</summary>

`usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`。這會讓呼叫端可以傳入任何值，包括非函式，可能導致執行時期錯誤（例如 `useContextSelector` 內部呼叫 selector 時拋出錯誤）。建議保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => any` 以維持型別檢查。

**判斷依據**：diff 中此行由 `export function usePluginPageContext(selector: (value: PluginPageContextValue) => any) {` 改為 `export function usePluginPageContext(selector: any) {`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3172 (cache hit 3072) ｜ completion tokens 745 ｜ PR #9</sub>