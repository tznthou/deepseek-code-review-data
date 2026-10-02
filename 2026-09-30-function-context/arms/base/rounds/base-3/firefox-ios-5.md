<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Firefox iOS 中「非活躍分頁（Inactive Tabs）」的完整功能，包含相關的 Model、View、Middleware、State、輔助功能識別碼、字串與測試。整體而言，移除範圍完整且一致，但發現兩個潛在問題：1) 在 `TabsPanelState.createTabScrollBehavior` 中，當沒有選取分頁時，回傳的 `toIndex` 從 `state.tabs.count - 1` 改為 `state.tabs.count`，可能導致陣列索引越界；2) 在 `Strings.swift` 中，原本刪除的 Inactive Tabs 字串被重新加入至新的 `v147` 結構中，但未見任何使用，可能造成混淆或未來誤用。建議修正索引計算並確認字串的必要性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | scrollToTab 索引可能越界 | 0.90 |
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:8461` | 重新加入未使用的 Inactive Tabs 字串 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> scrollToTab 索引可能越界</summary>

在 `createTabScrollBehavior` 中，當沒有選取分頁且 `state.tabs` 不為空時，回傳的 `toIndex` 從 `state.tabs.count - 1` 改為 `state.tabs.count`。這會導致 `IndexPath(row:section:)` 使用超出陣列範圍的 row，進而在 `scrollToTab` 中嘗試滾動到不存在的索引，可能造成應用程式崩潰。

**失敗情境**：使用者開啟多個分頁，但沒有任何分頁被選取（例如剛啟動或切換面板後），此時觸發滾動到選取分頁的行為，就會嘗試滾動到 `tabs.count` 的索引，而陣列最後一個有效索引是 `tabs.count - 1`。

**建議**：改回 `state.tabs.count - 1`，或明確處理 `tabs` 為空的情況。

**判斷依據**：diff 中此行由 `return ScrollState(toIndex: state.tabs.count - 1, isInactiveTabSection: false, withAnimation: shouldAnimate)` 改為 `return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`，移除了 `-1`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 重新加入未使用的 Inactive Tabs 字串</summary>

在 `Strings.swift` 中，原本刪除的 Inactive Tabs 相關字串被重新加入至新的 `v147` 結構中，但程式碼中已無任何使用這些字串的地方。這可能造成混淆，且若未來誤用可能導致功能回歸。

**建議**：確認這些字串是否真的需要保留。若無使用，應一併刪除；若為了向後相容或未來功能，應加上明確註解。

**判斷依據**：diff 中刪除了 `InactiveTabs` 結構，但在 `v147` 結構中重新加入了相同的字串常數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 26423 (cache hit 26368) ｜ completion tokens 1225 ｜ PR #5</sub>