<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 marketplace 的搜尋狀態從可選的 atom/URL 雙軌制改為一律使用 URL query（nuqs），並移除了相關的 hydration 元件與 atom。主要風險在於 `useMarketplaceSearchMode` 中布林邏輯的變更（移除 `!`）可能導致搜尋模式判斷錯誤，以及 `usePluginPageContext` 的 selector 型別從函式放寬為 `any`，喪失型別安全。建議先確認這兩個變更的意圖與影響。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:43` | 布林邏輯變更可能導致搜尋模式判斷錯誤 | 0.80 |
| 🔸 | Minor | `web/app/components/plugins/plugin-page/context.tsx:51` | selector 型別放寬為 any 喪失型別安全 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 布林邏輯變更可能導致搜尋模式判斷錯誤</summary>

原本的條件是 `(searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，現在變成 `(searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。這會反轉當 `searchMode` 為 null/undefined 時的預設行為：原本不在集合中的分類會進入搜尋模式，現在變成在集合中的分類才會進入搜尋模式。請確認此變更是否為預期，否則可能導致 marketplace 在非搜尋情境下錯誤顯示搜尋模式。

**判斷依據**：diff 中此行由 `|| (searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))` 改為 `|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了邏輯 NOT。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> selector 型別放寬為 any 喪失型別安全</summary>

`usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會讓呼叫端可以傳入任何值，失去編譯時期的型別檢查。若傳入非函式，`useContextSelector` 可能拋出錯誤或產生非預期行為。建議保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => unknown`。

**判斷依據**：diff 中此行由 `export function usePluginPageContext(selector: (value: PluginPageContextValue) => any) {` 改為 `export function usePluginPageContext(selector: any) {`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3172 (cache hit 3072) ｜ completion tokens 712 ｜ PR #9</sub>