<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 的搜尋狀態從可選的 URL 保留改為一律保留在 URL 中，並移除了相關的 atom 與 hydration 元件。主要風險在於 `useMarketplaceSearchMode` 中布林邏輯的變更（移除 `!`）可能導致搜尋模式判斷錯誤，以及 `usePluginPageContext` 的 selector 參數型別從函式放寬為 `any`，違反 R09 並降低型別安全。建議先修正這兩個問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 布林邏輯錯誤：移除 `!` 導致搜尋模式判斷相反 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] 使用 `any` 型別作為 selector 參數，降低型別安全 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 布林邏輯錯誤：移除 `!` 導致搜尋模式判斷相反</summary>

在 `useMarketplaceSearchMode` 中，原本的條件是 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，但此 PR 移除了 `!`，變成 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。這會讓「當 activePluginType 屬於有 collections 的類別時，即使沒有搜尋文字或 tags，也會被視為搜尋模式」，反之亦然。這很可能導致 UI 顯示錯誤的搜尋模式，例如在一般瀏覽時顯示搜尋結果頁面。

建議：確認此變更是否為預期行為。若原本的邏輯是正確的，請恢復 `!`；若是有意變更，請提供說明並更新相關測試。

**判斷依據**：diff 中此行從 `|| (searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))` 改為 `|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] 使用 `any` 型別作為 selector 參數，降低型別安全</summary>

`usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`。這違反了 R09（避免使用 `any`），且會讓呼叫端可以傳入任意值，失去型別檢查。

建議：保留原本的函式型別，或使用更精確的泛型來描述 selector。

**判斷依據**：diff 中此行從 `export function usePluginPageContext(selector: (value: PluginPageContextValue) => any) {` 改為 `export function usePluginPageContext(selector: any) {`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5851 (cache hit 5760) ｜ completion tokens 750 ｜ PR #9</sub>