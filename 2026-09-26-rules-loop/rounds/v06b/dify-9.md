<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 marketplace 的搜尋狀態從可選的 URL 保留改為一律保留在 URL 中，並移除了相關的 Jotai atoms 與 hydration 元件。主要風險在於 `usePluginPageContext` 的 selector 參數型別從具體函式改為 `any`，違反 R09，可能導致型別安全漏洞。另外，`useMarketplaceSearchMode` 中布林邏輯的變更（移除 `!`）可能改變搜尋模式的判斷，需確認是否為預期行為。整體而言，重構方向合理，但需修正型別問題並驗證邏輯變更。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] 使用 `any` 型別作為 selector 參數 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:43` | 布林邏輯變更可能影響搜尋模式判斷 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] 使用 `any` 型別作為 selector 參數</summary>

`usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會完全喪失型別檢查，可能導致傳入錯誤的 selector 而引發執行時期錯誤。建議保留原本的函式型別，或使用更精確的泛型來約束 selector。

**判斷依據**：diff 中將原本的 `(value: PluginPageContextValue) => any` 改為 `any`，違反 R09。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 布林邏輯變更可能影響搜尋模式判斷</summary>

原本的條件是 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，現在改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`（移除了 `!`）。這會反轉判斷結果，可能導致搜尋模式在非預期的情況下被啟用或停用。請確認此變更是否為預期行為，並補充對應的測試。

**判斷依據**：diff 中該行從 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5841 (cache hit 5760) ｜ completion tokens 640 ｜ PR #9</sub>