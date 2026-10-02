<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 的搜尋狀態從可選的 atom 切換為一律使用 URL query，並移除了相關的 hydration 元件。主要風險在於 `useMarketplaceSearchMode` 中條件判斷的邏輯反轉，可能導致搜尋模式判斷錯誤；此外 `usePluginPageContext` 的型別從函式放寬為 any，降低型別安全。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 搜尋模式判斷邏輯反轉 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | 型別安全降低：selector 參數從函式改為 any | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 搜尋模式判斷邏輯反轉</summary>

在 `useMarketplaceSearchMode` 中，原本的條件是 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，但此 PR 移除了 `!`，變成 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。這會導致當 activePluginType 屬於有 collections 的類別時，即使沒有搜尋文字或 tags，也會被誤判為搜尋模式；反之，不屬於有 collections 的類別時，即使有搜尋文字或 tags，也可能不被視為搜尋模式。這將直接影響 UI 顯示與資料載入邏輯。

**判斷依據**：diff 中此行由 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> 型別安全降低：selector 參數從函式改為 any</summary>

`usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會失去對 selector 函式的型別檢查，可能導致傳入非函式值時在執行階段出錯，或無法在編譯期發現錯誤的 selector 實作。建議保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => unknown` 並在內部進行型別斷言。

**判斷依據**：diff 中此行由 `selector: (value: PluginPageContextValue) => any` 改為 `selector: any`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3318 (cache hit 3200) ｜ completion tokens 661 ｜ PR #9</sub>