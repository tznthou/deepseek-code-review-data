<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Inactive Tabs 功能，包含相關的模型、視圖、狀態管理、輔助功能識別碼、本地化字串與測試。整體刪除範圍完整，但發現一個明確的 off-by-one 錯誤：在 `TabsPanelState.createTabScrollBehavior` 中，當沒有選取的 tab 時，回傳的 `toIndex` 從 `state.tabs.count - 1` 改為 `state.tabs.count`，這會導致滾動到超出陣列範圍的索引，可能造成越界存取或滾動失敗。此外，`TabDisplayView.scrollToTab` 中 section 固定為 1，但現在只有一個 section（index 0），這會導致滾動到不存在的 section，功能失效。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | off-by-one 錯誤：滾動索引超出陣列範圍 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172` | 滾動目標 section 固定為 1，但現在只有一個 section | 0.90 |
| 🔸 | Minor | `firefox-ios/Shared/Strings.swift:8461` | 新增的 v147 結構體可能未被使用 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> off-by-one 錯誤：滾動索引超出陣列範圍</summary>

在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，原本回傳 `state.tabs.count - 1`，但此 PR 改為 `state.tabs.count`。這會導致 `toIndex` 等於陣列長度，超出有效索引範圍（最後一個索引應為 `count - 1`）。後續在 `TabDisplayView.scrollToTab` 中會使用此索引建立 `IndexPath(row:section:)`，可能造成滾動到不存在的 cell，甚至觸發越界例外。

建議改回 `state.tabs.count - 1`。

**判斷依據**：diff 中此行由 `return ScrollState(toIndex: state.tabs.count - 1, isInactiveTabSection: false, withAnimation: shouldAnimate)` 改為 `return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`，移除了 `-1`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172</code> 滾動目標 section 固定為 1，但現在只有一個 section</summary>

在 `scrollToTab` 中，原本根據 `scrollState.isInactiveTabSection` 決定 section 為 0 或 1，現在直接寫死為 1。但移除 inactive tabs 後，collection view 只有一個 section（index 0），因此 `IndexPath(row:section:1)` 會指向不存在的 section，導致滾動功能失效。

建議將 section 改為 0。

**判斷依據**：diff 中此行由 `let section: Int = scrollState.isInactiveTabSection ? 0 : 1` 和 `let indexPath = IndexPath(row: scrollState.toIndex, section: section)` 改為直接寫死 `section: 1`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 新增的 v147 結構體可能未被使用</summary>

在 `String` 擴展中新增了 `struct v147`，其中包含原本屬於 `InactiveTabs` 的本地化字串。但這些字串在程式碼中已不再被引用（因為相關視圖已刪除），可能成為死代碼。若確認不再需要，應一併移除；若仍需要保留以供未來使用，建議加上註解說明。

**判斷依據**：diff 中新增了 `struct v147`，但搜尋整個 diff 未見任何地方引用這些靜態屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 26423 (cache hit 1536) ｜ completion tokens 1007 ｜ PR #5</sub>