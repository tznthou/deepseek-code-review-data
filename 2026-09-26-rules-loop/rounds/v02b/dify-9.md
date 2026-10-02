<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 marketplace 搜尋狀態從可選的 URL 保留改為一律保留在 URL 中，移除了相關的 atom 與 hydration 元件，並將 activePluginType 的 query key 從 'category' 改為 'tab'。主要風險在於 query key 變更可能造成既有書籤或分享連結失效，以及移除 preserveSearchStateInQuery 後，原本依賴 atom 狀態的元件行為可能改變。此外，usePluginPageContext 的 selector 參數型別從具體函式改為 any，違反了專案的型別安全規範。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] 使用 any 型別違反 TypeScript 型別安全規範 | 0.90 |
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:22` | query key 從 'category' 改為 'tab' 可能破壞既有 URL 相容性 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] 使用 any 型別違反 TypeScript 型別安全規範</summary>

selector 參數的型別從具體的函式型別改為 any，這會失去型別檢查，可能導致 runtime 錯誤。應保留原本的函式型別，或使用更精確的型別定義。

**判斷依據**：diff 中將 selector 的型別從 (value: PluginPageContextValue) => any 改為 any。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:22</code> query key 從 'category' 改為 'tab' 可能破壞既有 URL 相容性</summary>

原本使用 'category' 作為 query parameter 來保存 activePluginType，現在改為 'tab'。這會導致任何已分享或書籤的 URL（例如 ?category=xxx）失效，使用者會回到預設的 'all' 分類。若此變更是有意為之，應考慮加入相容性處理（例如同時讀取 'category' 與 'tab'，或進行 redirect）。

**判斷依據**：diff 中將 useQueryState 的第一個參數從 'category' 改為 'tab'。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5851 (cache hit 5760) ｜ completion tokens 574 ｜ PR #9</sub>