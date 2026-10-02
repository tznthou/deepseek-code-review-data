<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 的搜尋狀態從可選的 URL 保留改為一律使用 URL query，並移除了相關的 atom 與 hydration 元件。主要風險在於 `useMarketplaceSearchMode` 中條件判斷的邏輯反轉，可能導致搜尋模式判斷錯誤；另外 `usePluginPageContext` 的型別從函式改為 `any`，喪失型別安全。整體改動方向合理，但需修正上述問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 搜尋模式判斷邏輯反轉 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | 喪失型別安全：selector 參數改為 any | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 搜尋模式判斷邏輯反轉</summary>

在 `useMarketplaceSearchMode` 中，原本的條件 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 被改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，少了否定運算子。這會導致當 `activePluginType` 屬於有 collections 的類別時，`searchMode` 會被設為 `true`，反之則為 `false`，與預期行為完全相反。例如，若使用者選擇一個有 collections 的類別且沒有輸入搜尋文字或標籤，原本應顯示 collections 列表，現在卻會進入搜尋模式，顯示空結果或錯誤內容。

建議將條件改回 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。

**判斷依據**：diff 中此行將原本的 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了否定運算子。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> 喪失型別安全：selector 參數改為 any</summary>

`usePluginPageContext` 的參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會讓 TypeScript 無法檢查傳入的 selector 是否為函式，也無法推斷回傳值型別。若呼叫端誤傳非函式值，將在執行時期拋出錯誤，且編譯器無法攔截。建議保留原本的函式型別，或使用更精確的泛型來保留型別推斷。

**判斷依據**：diff 中將 `selector: (value: PluginPageContextValue) => any` 改為 `selector: any`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3318 (cache hit 1536) ｜ completion tokens 719 ｜ PR #9</sub>