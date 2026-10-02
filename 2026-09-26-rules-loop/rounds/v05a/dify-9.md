<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 marketplace 搜尋狀態從可選的 URL 保留改為一律保留在 URL 中，並移除了相關的 atom 與 hydration 元件。主要風險在於 `usePluginPageContext` 的 selector 參數型別從具體函式放寬為 `any`，違反 R09 且可能導致型別安全漏洞。另外，`useMarketplaceSearchMode` 中移除了一個否定運算子，可能改變搜尋模式的判斷邏輯，需確認是否為預期行為。整體而言，變更方向合理，但需修正型別問題並驗證邏輯變更。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] selector 參數型別從具體函式放寬為 any | 0.90 |
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:43` | 搜尋模式判斷邏輯可能反轉 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] selector 參數型別從具體函式放寬為 any</summary>

`usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會完全喪失型別檢查，允許傳入任意值，可能導致執行時期錯誤。建議保留原本的函式型別，或使用更精確的泛型型別。

**判斷依據**：diff 中將原本的 `(value: PluginPageContextValue) => any` 改為 `any`，違反 R09 規範。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 搜尋模式判斷邏輯可能反轉</summary>

原本的條件是 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，現在改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了否定運算子。這可能導致 `isSearchMode` 的判斷結果相反，影響搜尋模式的啟用時機。請確認此變更是否為預期行為，並補充對應的測試。

**判斷依據**：diff 中將 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5771 (cache hit 3072) ｜ completion tokens 626 ｜ PR #9</sub>