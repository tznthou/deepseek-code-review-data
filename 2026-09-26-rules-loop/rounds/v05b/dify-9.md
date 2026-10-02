<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 marketplace 搜尋狀態從可選的 URL 保留改為一律保留在 URL 中，並移除了相關的 atom 與 hydration 元件。主要風險在於 `usePluginPageContext` 的 selector 參數型別從具體函式放寬為 `any`，違反 R09，可能導致型別安全問題。另外 `useMarketplaceSearchMode` 中條件判斷的邏輯變更（移除 `!`）需要確認是否為預期行為。整體而言，改動方向合理，但需修正型別問題並確認邏輯變更。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] 使用 any 型別作為 selector 參數 | 0.90 |
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:43` | 搜尋模式條件邏輯變更可能導致行為錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] 使用 any 型別作為 selector 參數</summary>

將 `selector` 參數型別從具體函式改為 `any`，違反 R09（TypeScript Must Avoid any Type Annotations）。這會失去型別檢查，可能導致傳入錯誤的 selector 函式而未被發現。建議保留原本的函式型別，或使用更精確的泛型型別。

**判斷依據**：diff 中將 `selector: (value: PluginPageContextValue) => any` 改為 `selector: any`，直接違反 R09。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 搜尋模式條件邏輯變更可能導致行為錯誤</summary>

原本條件為 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，現在改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`（移除 `!`）。這會反轉判斷結果，可能導致搜尋模式判斷錯誤。請確認此變更是否為預期，若非預期則應保留原本的否定。

**判斷依據**：diff 中該行從 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5771 (cache hit 5760) ｜ completion tokens 615 ｜ PR #9</sub>