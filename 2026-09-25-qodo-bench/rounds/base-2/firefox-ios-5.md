<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 Inactive Tabs 功能，包含相關的模型、視圖、狀態管理、輔助功能識別碼與測試。整體刪除範圍完整，但發現兩個潛在問題：`TabsPanelState.createTabScrollBehavior` 中 `toIndex` 的 off-by-one 錯誤，以及 `Strings.swift` 中新增的 `v147` 結構體可能造成重複定義。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | scrollToTab 的 toIndex 可能越界 | 0.90 |
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:8461` | 新增的 v147 結構體可能造成重複定義 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> scrollToTab 的 toIndex 可能越界</summary>

在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，回傳的 `toIndex` 為 `state.tabs.count`，但陣列索引應為 `count - 1`。這會導致滾動到不存在的索引，可能造成 collection view 崩潰或滾動到錯誤位置。

建議改為 `state.tabs.count - 1`。

**判斷依據**：diff 中此行將原本的 `state.tabs.count - 1` 改為 `state.tabs.count`，但未調整其他邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 新增的 v147 結構體可能造成重複定義</summary>

在 `String.TabsTray` 中新增了 `struct v147`，其中包含與先前刪除的 `InactiveTabs` 結構體相同的靜態屬性。若專案中其他地方已存在 `v147` 結構體，或未來版本更新時可能衝突。建議確認此結構體名稱的唯一性，或考慮使用更明確的名稱。

**判斷依據**：diff 中新增了 `struct v147`，且其內容與刪除的 `InactiveTabs` 結構體重複。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 26423 (cache hit 26368) ｜ completion tokens 559 ｜ PR #5</sub>