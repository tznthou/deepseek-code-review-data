<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 marketplace 搜尋狀態從可選的 URL 保留改為一律使用 URL query state，移除了 preserveSearchStateInQueryAtom 與 HydrateMarketplaceAtoms，並將 activePluginType 的 query key 從 'category' 改為 'tab'。主要風險在於 query key 變更可能破壞現有 URL 或外部連結，且移除條件式保留後，所有 marketplace 實例都將依賴 URL 參數，若未提供 searchParams 可能導致狀態遺失。另有 usePluginPageContext 的 selector 參數型別從函式改為 any，違反 R09。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/plugins/marketplace/atoms.ts:23` | activePluginType 的 query key 從 'category' 改為 'tab' 可能破壞現有 URL | 0.80 |
| 🔸 | Minor | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] usePluginPageContext 的 selector 參數使用 any 型別 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/marketplace/atoms.ts:23</code> activePluginType 的 query key 從 'category' 改為 'tab' 可能破壞現有 URL</summary>

原本使用 'category' 作為 query parameter，現在改為 'tab'。這會導致任何已分享或書籤的 URL 使用舊的 'category' 參數時，狀態無法正確讀取，使用者會回到預設的 'all' 分類。建議保留 'category' 或加入相容性處理（例如同時讀取兩個 key）。

**判斷依據**：diff 中將 'category' 改為 'tab'，且未見任何相容性處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] usePluginPageContext 的 selector 參數使用 any 型別</summary>

selector 參數從具體的函式型別改為 any，違反 R09（避免 any 型別）。這會失去型別檢查，可能導致呼叫端傳入錯誤的 selector 而不被發現。建議保留原本的函式型別或使用更精確的泛型。

**判斷依據**：diff 中將 selector 的型別從 (value: PluginPageContextValue) => any 改為 any。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5851 (cache hit 1536) ｜ completion tokens 575 ｜ PR #9</sub>