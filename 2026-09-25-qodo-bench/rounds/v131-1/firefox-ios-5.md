<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Firefox iOS 中「非活躍分頁（Inactive Tabs）」功能的相關程式碼，包括模型、視圖、狀態管理、輔助功能識別碼、本地化字串與測試。整體而言，移除範圍完整，但發現一個潛在的索引錯誤：在 `TabsPanelState.createTabScrollBehavior` 中，當沒有選取分頁時，回傳的 `toIndex` 使用了 `state.tabs.count`，這會導致索引超出範圍，可能造成滾動到錯誤位置或當機。建議修正為 `state.tabs.count - 1`。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | 滾動索引超出範圍 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> 滾動索引超出範圍</summary>

在 `createTabScrollBehavior` 中，當沒有選取分頁時，回傳的 `toIndex` 使用了 `state.tabs.count`，但陣列索引是從 0 開始，因此最後一個有效索引是 `count - 1`。這會導致 `IndexPath(row:section:)` 使用無效的 row，可能造成滾動到錯誤位置或當機。

建議改為 `state.tabs.count - 1`。

**判斷依據**：diff 中此行由原本的 `state.tabs.count - 1` 改為 `state.tabs.count`，且測試 `testCreateTabScrollBehavior_forScrollToSelectedTab_noSelectedTab_returnsLastTab_ifTabsNotEmpty` 仍預期 `toIndex` 為 `tabCount - 1`，但測試尚未更新，可能導致測試失敗。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 26387 (cache hit 1408) ｜ completion tokens 451 ｜ PR #5</sub>