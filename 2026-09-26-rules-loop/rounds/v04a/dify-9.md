<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 搜尋狀態從可選的 URL 保留改為一律保留在 URL，並移除了相關的 atom 與 hydration 元件。主要風險在於 `usePluginPageContext` 的 selector 參數型別從函式改為 `any`，違反 R09 且喪失型別安全；另外 `useMarketplaceSearchMode` 的條件判斷被反轉，可能導致搜尋模式判斷錯誤。整體而言，變更方向合理，但需修正上述問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] selector 參數型別從函式改為 any，喪失型別安全 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:43` | 搜尋模式判斷條件被反轉，可能導致錯誤的搜尋模式 | 0.85 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] selector 參數型別從函式改為 any，喪失型別安全</summary>

`usePluginPageContext` 的 selector 參數原本是 `(value: PluginPageContextValue) => any`，現在改成 `any`，這會讓呼叫端可以傳入任意值，繞過 TypeScript 的型別檢查，違反 R09。建議保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => unknown` 並在內部處理。

**判斷依據**：diff 中將 `selector: (value: PluginPageContextValue) => any` 改為 `selector: any`，且 repo 規範 R09 明確禁止 any。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 搜尋模式判斷條件被反轉，可能導致錯誤的搜尋模式</summary>

原本的條件是 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，現在改成 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，邏輯相反。這會讓原本不屬於集合的類別被視為搜尋模式，而屬於集合的類別反而被視為非搜尋模式，可能影響 UI 顯示或資料載入。請確認此變更是否為預期，若不是則應改回原本的否定。

**判斷依據**：diff 中將 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，且未見其他配套修改。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4412 (cache hit 3072) ｜ completion tokens 660 ｜ PR #9</sub>