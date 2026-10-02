<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Firefox iOS 中「非活躍分頁（Inactive Tabs）」的完整功能，包含相關的模型、視圖、狀態管理、輔助功能識別碼、本地化字串與測試。整體而言，移除範圍相當完整，但存在兩個主要風險：1) `TabsPanelState.createTabScrollBehavior` 中滾動到最後一個分頁的索引計算有 off-by-one 錯誤，可能導致滾動到錯誤位置或越界；2) 本地化字串被移入 `v147` 結構中，但該結構可能未被正確使用，且舊的 key 仍被保留，可能造成混淆。建議修正滾動索引計算，並確認本地化字串的引用方式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | 滾動到最後一個分頁時索引計算錯誤 | 0.95 |
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:8461` | 本地化字串被移入未使用的 v147 結構 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172` | 滾動 section 索引硬編碼為 1，可能導致錯誤 | 0.75 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | 滾動到最後一個分頁的索引計算可能與預期不符 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> 滾動到最後一個分頁時索引計算錯誤</summary>

在 `createTabScrollBehavior` 中，當沒有選中的分頁且分頁列表不為空時，原本回傳 `state.tabs.count - 1`，但修改後變成 `state.tabs.count`。這會導致 `IndexPath(row:section:)` 的 row 超出陣列範圍，可能造成滾動到不存在的索引或應用程式當機。

**失敗情境**：使用者切換到沒有選中分頁的分頁面板（例如從一般分頁切換到私密分頁），且分頁數量為 N。此時 `scrollState.toIndex` 會被設為 N，但有效的 row 索引範圍是 0...N-1。後續 `scrollToTab` 會建立 `IndexPath(row: N, section: 1)`，可能導致滾動到錯誤位置或觸發例外。

**建議修正**：將 `return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)` 改回 `return ScrollState(toIndex: state.tabs.count - 1, withAnimation: shouldAnimate)`。

**判斷依據**：diff 中 `TabsPanelState.swift` 的變更：原本 `return ScrollState(toIndex: state.tabs.count - 1, isInactiveTabSection: false, withAnimation: shouldAnimate)` 被改為 `return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 本地化字串被移入未使用的 v147 結構</summary>

原本在 `String.TabsTray.InactiveTabs` 中的四個本地化字串被移入 `String.TabsTray.v147` 結構中，但程式碼中已無任何地方引用這些字串（因為相關功能已移除）。這可能導致：
1. 這些字串永遠不會被使用，造成死代碼。
2. 如果未來需要重新引入類似功能，開發者可能找不到這些字串。
3. 舊的 key（如 `TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103`）仍被保留，可能造成混淆。

**建議**：確認這些字串是否真的不再需要。如果確定不需要，應完全刪除；如果未來可能使用，應考慮更合適的組織方式，並加上註解說明。

**判斷依據**：diff 中 `Strings.swift` 的變更：原本在 `InactiveTabs` 結構中的四個靜態屬性被刪除，並在 `v147` 結構中重新加入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172</code> 滾動 section 索引硬編碼為 1，可能導致錯誤</summary>

在 `scrollToTab` 方法中，原本根據 `scrollState.isInactiveTabSection` 決定 section 索引（0 或 1），現在直接硬編碼為 `section: 1`。由於移除了非活躍分頁 section，現在只有一個 section（索引 0），因此使用 `section: 1` 會導致 `IndexPath(row:section:)` 指向不存在的 section，可能造成滾動失敗或應用程式當機。

**失敗情境**：任何觸發滾動到分頁的操作（例如從外部點擊分頁）都會建立 `IndexPath(row: someRow, section: 1)`，但 collection view 只有一個 section（索引 0），因此滾動可能無效或拋出例外。

**建議修正**：將 `section: 1` 改為 `section: 0`。

**判斷依據**：diff 中 `TabDisplayView.swift` 的變更：原本 `let section: Int = scrollState.isInactiveTabSection ? 0 : 1` 被移除，改為直接使用 `section: 1`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> 滾動到最後一個分頁的索引計算可能與預期不符</summary>

在 `createTabScrollBehavior` 中，當沒有選中的分頁且分頁列表不為空時，回傳 `state.tabs.count` 作為 `toIndex`。這可能導致滾動到最後一個分頁之後的位置，而不是最後一個分頁本身。雖然這可能不會造成當機，但使用者體驗可能不佳。

**建議**：改回 `state.tabs.count - 1`。

**判斷依據**：diff 中 `TabsPanelState.swift` 的變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 26387 (cache hit 26368) ｜ completion tokens 1617 ｜ PR #5</sub>