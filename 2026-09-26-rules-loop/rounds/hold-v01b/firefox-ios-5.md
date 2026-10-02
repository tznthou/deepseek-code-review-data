<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Firefox iOS 中的 Inactive Tabs 功能，包括相關的模型、視圖、狀態管理、輔助功能識別碼、本地化字串及測試。整體而言，移除範圍完整，但存在兩個主要問題：一是在 `TabsPanelState.swift` 中，當沒有選取的 tab 時，滾動目標索引從 `state.tabs.count - 1` 改為 `state.tabs.count`，這可能導致陣列越界；二是在 `Strings.swift` 中，被刪除的本地化字串被重新加入到一個新的 `v147` 結構中，但該結構未標記為 `public`，且其用途不明，可能導致編譯錯誤或無效程式碼。建議修正這兩個問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | 滾動索引可能越界：`toIndex` 應為 `state.tabs.count - 1` | 0.95 |
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:8461` | 新增的 `v147` 結構未標記為 `public`，且可能包含無效的本地化鍵 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> 滾動索引可能越界：`toIndex` 應為 `state.tabs.count - 1`</summary>

在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，原本回傳 `state.tabs.count - 1`，但此 PR 改為 `state.tabs.count`。若 `state.tabs` 非空，`state.tabs.count` 會超出陣列最後一個元素的索引，導致後續使用 `IndexPath(row:section:)` 時可能觸發越界例外或滾動到不存在的 cell。

**失敗情境**：使用者開啟 tab 面板，沒有任何 tab 被選取（例如剛刪除選取的 tab），且 `state.tabs` 有 3 個元素。此時 `toIndex` 會被設為 3，但有效索引範圍是 0...2。

**建議修法**：改回 `state.tabs.count - 1`。

**判斷依據**：diff 中此行由 `return ScrollState(toIndex: state.tabs.count - 1, isInactiveTabSection: false, withAnimation: shouldAnimate)` 改為 `return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`，且 `state.tabs` 在此分支中保證非空（前一行有 `else if !state.tabs.isEmpty`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 新增的 `v147` 結構未標記為 `public`，且可能包含無效的本地化鍵</summary>

此 PR 刪除了 `String.TabsTray.InactiveTabs` 中的本地化字串，但在 `String.TabsTray` 下新增了一個 `v147` 結構，內容與被刪除的字串完全相同。然而，該結構沒有 `public` 修飾詞，且其名稱 `v147` 似乎只是版本標記，並非有意義的命名空間。這可能導致其他模組無法存取這些字串，且若這些鍵已不再使用，保留它們會造成混淆。

**失敗情境**：若有其他程式碼嘗試透過 `String.TabsTray.v147.TabsTrayInactiveTabsSectionClosedAccessibilityTitle` 存取，會因為 `v147` 不是 `public` 而編譯失敗。

**建議修法**：確認這些字串是否仍被使用。若已不再使用，應完全刪除；若仍需保留，應將其放在適當的 `public` 結構中，並使用有意義的名稱。

**判斷依據**：diff 中新增了 `struct v147 { ... }`，但未加上 `public` 修飾詞，且其內容與被刪除的 `InactiveTabs` 結構相同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 28482 (cache hit 28416) ｜ completion tokens 1065 ｜ PR #5</sub>