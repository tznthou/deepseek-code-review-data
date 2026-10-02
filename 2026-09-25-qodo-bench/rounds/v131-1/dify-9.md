<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 的搜尋狀態從可選的 atom/URL 雙軌制改為一律使用 URL query，並移除了 hydration 元件。主要風險在於 `useMarketplaceSearchMode` 中布林邏輯的變更（移除 `!`）可能反轉搜尋模式的判斷，且 `usePluginPageContext` 的 selector 型別從函式放寬為 `any`，喪失型別安全。建議先確認布林邏輯變更的意圖，並恢復 selector 的型別。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 布林邏輯變更可能反轉搜尋模式判斷 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | selector 型別從函式放寬為 any，喪失型別安全 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 布林邏輯變更可能反轉搜尋模式判斷</summary>

在 `useMarketplaceSearchMode` 中，原本的條件是 `(searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，現在改為 `(searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。這會導致當 `searchMode` 為 `null` 或 `undefined` 時，判斷結果完全相反：原本不在集合中的分類會被視為搜尋模式，現在變成在集合中的分類才會被視為搜尋模式。這很可能造成 UI 顯示錯誤（例如搜尋模式指示燈、列表行為）。請確認此變更是否為預期，若非預期請恢復 `!`。

**判斷依據**：diff 中此行由 `|| (searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))` 改為 `|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了邏輯 NOT。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> selector 型別從函式放寬為 any，喪失型別安全</summary>

`usePluginPageContext` 的參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會讓 TypeScript 無法檢查傳入的 selector 是否為函式，可能導致 runtime 錯誤（例如傳入非函式值）。建議保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => any` 或更精確的泛型。

**判斷依據**：diff 中此行由 `export function usePluginPageContext(selector: (value: PluginPageContextValue) => any) {` 改為 `export function usePluginPageContext(selector: any) {`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3136 (cache hit 1408) ｜ completion tokens 744 ｜ PR #9</sub>