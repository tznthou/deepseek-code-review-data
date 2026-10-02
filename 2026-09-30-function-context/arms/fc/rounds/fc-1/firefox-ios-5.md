<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Inactive Tabs 功能，包含相關的模型、視圖、狀態管理、動作與測試。整體刪除範圍完整，但有一個明確的 off-by-one 錯誤：在 `TabsPanelState.createTabScrollBehavior` 中，當沒有選取分頁時，回傳的 `toIndex` 是 `state.tabs.count`，這會導致索引超出範圍，可能造成滾動失敗或越界存取。此外，部分 XCUITest 中的 cell identifier 從 section 1 改為 section 0，需確認與新的 section 結構一致。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | scrollToTab 的 toIndex 可能超出範圍 | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/XCUITests/TabsTests.swift:49` | XCUITest 中的 cell identifier 可能與新的 section 結構不符 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> scrollToTab 的 toIndex 可能超出範圍</summary>

在 `createTabScrollBehavior` 中，當沒有選取分頁時，回傳 `ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`。陣列索引是從 0 開始，最後一個有效索引是 `count - 1`，因此 `count` 會超出範圍。這會導致 `scrollToTab` 中的 `IndexPath(row:section:)` 無效，可能造成滾動失敗或越界存取。

建議改為 `state.tabs.count - 1`。

**判斷依據**：diff 中此行由原本的 `state.tabs.count - 1` 改為 `state.tabs.count`，且下方 `scrollToTab` 使用此 index 建立 `IndexPath`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/XCUITests/TabsTests.swift:49</code> XCUITest 中的 cell identifier 可能與新的 section 結構不符</summary>

多處測試將 cell identifier 從 `_1_` 改為 `_0_`，例如 `TabDisplayView.tabCell_0_1`。但 `TabDisplayDiffableDataSource` 現在只有一個 section（`.tabs`），因此 section index 應為 0。然而，需確認 `TabDisplayView` 的 `collectionView` 是否還有其他 section（例如 header/footer 可能佔用 section 0），否則測試可能找不到正確的 cell。

建議執行相關 XCUITest 驗證。

**判斷依據**：diff 中多處將 `_1_` 改為 `_0_`，但未提供 section 結構的完整變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 72279 (cache hit 1536) ｜ completion tokens 706 ｜ PR #5</sub>