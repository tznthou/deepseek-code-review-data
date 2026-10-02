<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 marketplace 的搜尋狀態從可選的 atom 儲存改為一律使用 URL query 參數，並刪除了 hydration-client 與相關 atom。主要風險在於 `usePluginPageContext` 的 selector 型別從具體函式放寬為 `any`，違反 R09，可能導致型別安全喪失。另外 `useMarketplaceSearchMode` 中布林邏輯的變更（移除 `!`）需要確認是否為預期行為。整體而言，變更方向合理，但需修正型別問題並確認邏輯正確性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] 使用 `any` 型別作為 selector 參數 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:43` | 布林邏輯變更可能導致搜尋模式判斷錯誤 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] 使用 `any` 型別作為 selector 參數</summary>

`usePluginPageContext` 的 selector 參數型別從具體函式改為 `any`，這會繞過 TypeScript 的型別檢查，可能導致執行時期錯誤。建議保留原本的函式型別，或使用泛型來維持型別安全。

**判斷依據**：diff 中將 `selector: (value: PluginPageContextValue) => any` 改為 `selector: any`，違反 R09。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 布林邏輯變更可能導致搜尋模式判斷錯誤</summary>

原本的條件是 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，現在改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`（移除了 `!`）。這會反轉判斷結果：原本在非集合類別時視為搜尋模式，現在變成在集合類別時視為搜尋模式。請確認這是否為預期行為。

**判斷依據**：diff 中該行從 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5841 (cache hit 3072) ｜ completion tokens 614 ｜ PR #9</sub>