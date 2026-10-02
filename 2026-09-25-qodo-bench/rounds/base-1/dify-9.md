<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除 marketplace 搜尋狀態的 Jotai atom 與 hydration 機制，改為一律使用 URL query state（nuqs），並將 activePluginType 的 query key 從 'category' 改為 'tab'。主要風險在於 query key 變更可能破壞既有書籤或分享連結，且 useMarketplaceSearchMode 中移除否定運算子可能反轉搜尋模式判斷邏輯。此外，usePluginPageContext 的 selector 參數型別從函式放寬為 any，喪失型別安全。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:43` | 移除否定運算子可能反轉搜尋模式判斷 | 0.80 |
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:23` | query key 從 'category' 改為 'tab' 可能破壞既有連結 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/plugin-page/context.tsx:51` | selector 參數型別從函式放寬為 any，喪失型別安全 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 移除否定運算子可能反轉搜尋模式判斷</summary>

在 `useMarketplaceSearchMode` 中，原本 `!(PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType))` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了否定運算子。這會導致當 activePluginType 屬於 PLUGIN_CATEGORY_WITH_COLLECTIONS 時，原本應為非搜尋模式，現在卻會被視為搜尋模式，反之亦然。請確認此變更是否為預期行為，若非預期，請恢復否定運算子。

**判斷依據**：diff 中此行由 `|| (searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))` 改為 `|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:23</code> query key 從 'category' 改為 'tab' 可能破壞既有連結</summary>

`useActivePluginType` 的 query key 從 `'category'` 改為 `'tab'`。若使用者已將帶有 `?category=...` 的網址加入書籤或分享，升級後這些連結將不再生效，可能導致使用者看到非預期的分類。建議考慮保留舊 key 的相容性，或確認此變更為可接受的 breaking change。

**判斷依據**：diff 中 `useQueryState('category', ...)` 改為 `useQueryState('tab', ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> selector 參數型別從函式放寬為 any，喪失型別安全</summary>

`usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`。這會讓呼叫端可以傳入任意值，若傳入非函式，`useContextSelector` 可能拋出錯誤或產生非預期行為。建議保留原本的函式型別，或使用更精確的泛型。

**判斷依據**：diff 中此行由 `export function usePluginPageContext(selector: (value: PluginPageContextValue) => any) {` 改為 `export function usePluginPageContext(selector: any) {`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3172 (cache hit 1536) ｜ completion tokens 917 ｜ PR #9</sub>