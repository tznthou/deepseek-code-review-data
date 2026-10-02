<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Firefox iOS 中「非活躍分頁（Inactive Tabs）」的相關程式碼，包含模型、視圖、狀態管理、輔助功能識別碼與測試。整體刪除範圍完整，但發現一個明確的邏輯錯誤：在 `TabsPanelState.createTabScrollBehavior` 中，當沒有選取分頁時，回傳的索引從 `state.tabs.count - 1` 改成了 `state.tabs.count`，這會導致滾動到超出最後一個分頁的位置，可能造成滾動失敗或顯示空白。此外，部分字串被移至 `OldStrings.v147`，但未確認是否有其他程式碼仍在使用這些字串，可能導致編譯錯誤或遺漏清理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | 滾動索引 off-by-one：應為 `state.tabs.count - 1` 而非 `state.tabs.count` | 0.95 |
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:8461` | 字串移至 `OldStrings.v147` 但可能仍有使用 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> 滾動索引 off-by-one：應為 `state.tabs.count - 1` 而非 `state.tabs.count`</summary>

在 `createTabScrollBehavior` 中，當沒有選取分頁且 `tabs` 不為空時，原本回傳 `state.tabs.count - 1`（最後一個分頁的索引），但此 PR 改成了 `state.tabs.count`。這會導致 `scrollToTab` 嘗試滾動到不存在的索引，可能造成 `UICollectionView` 滾動失敗或顯示不正確的位置。

**失敗情境**：使用者開啟多個分頁但沒有選取任何分頁（例如剛切換到分頁面板），此時 `scrollState.toIndex` 會是 `tabs.count`，而 `collectionView` 的有效索引範圍是 `0..<tabs.count`，因此 `isValid(indexPath:)` 會回傳 `false`，導致不執行滾動。

**建議修法**：將該行改回 `return ScrollState(toIndex: state.tabs.count - 1, withAnimation: shouldAnimate)`。

**判斷依據**：diff 中 `TabsPanelState.swift` 的變更：
```
-                return ScrollState(toIndex: state.tabs.count - 1, isInactiveTabSection: false, withAnimation: shouldAnimate)
+                return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)
```

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 字串移至 `OldStrings.v147` 但可能仍有使用</summary>

此 PR 將 `TabsTrayInactiveTabsSectionClosedAccessibilityTitle`、`TabsTrayInactiveTabsSectionOpenedAccessibilityTitle`、`CloseAllInactiveTabsButton`、`CloseInactiveTabSwipeActionTitle` 從 `String.TabsTray.InactiveTabs` 移至 `String.OldStrings.v147`。然而，在刪除的程式碼中，這些字串曾被用於 `InactiveTabsHeaderView`、`InactiveTabsFooterView` 等檔案，但這些檔案已被刪除。需要確認是否還有其他未刪除的程式碼仍引用這些字串，否則可能導致編譯錯誤。

**建議**：搜尋整個程式碼庫，確認這些字串已無任何引用；若有引用，應一併移除或保留字串定義。

**判斷依據**：diff 中 `Strings.swift` 新增了 `OldStrings.v147` 區塊，包含上述字串。同時刪除了 `String.TabsTray.InactiveTabs` 結構，但未確認所有引用都已移除。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 72279 (cache hit 72192) ｜ completion tokens 1349 ｜ PR #5</sub>