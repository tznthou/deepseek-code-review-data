<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除 Inactive Tabs 功能，包含刪除相關檔案、狀態屬性、動作與 UI 元件，並更新測試。主要風險在於刪除後可能遺留未使用的程式碼或違反專案規範。最需優先確認的是 TabPanelAction.swift 中移除 MPL 標頭是否違反 R01，以及 TabsPanelState.swift 中 scrollToTab 的索引計算是否正確。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Tabs/Action/TabPanelAction.swift:1` | [R01] 移除 MPL 標頭違反授權規範 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | scrollToTab 索引計算可能錯誤 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172` | 硬編碼 section 索引可能導致錯誤 | 0.70 |
| 🔸 | Minor | `firefox-ios/Shared/Strings.swift:8461` | 新增 v147 結構可能違反組織慣例 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/Action/TabPanelAction.swift:1</code> [R01] 移除 MPL 標頭違反授權規範</summary>

此檔案原本有 Mozilla Public License 標頭，但在此 PR 中被移除。根據規範 R01，所有 Swift 檔案必須包含 MPL 標頭。請恢復標頭。

**判斷依據**：diff 顯示刪除了三行 MPL 標頭，且未新增替代標頭。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> scrollToTab 索引計算可能錯誤</summary>

在 `createTabScrollBehavior` 中，當找不到選取的 tab 且 tabs 不為空時，原本回傳 `state.tabs.count - 1`，但此 PR 改為 `state.tabs.count`。這可能導致索引超出範圍，因為陣列索引從 0 開始。請確認是否應為 `state.tabs.count - 1`。

**判斷依據**：diff 中將 `state.tabs.count - 1` 改為 `state.tabs.count`，且未調整其他邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172</code> 硬編碼 section 索引可能導致錯誤</summary>

在 `scrollToTab` 中，原本根據 `scrollState.isInactiveTabSection` 決定 section，現在固定為 1。若未來 section 順序變更，可能導致滾動到錯誤位置。建議使用更明確的 section 識別方式。

**判斷依據**：diff 顯示移除條件判斷，直接使用 section 1。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 新增 v147 結構可能違反組織慣例</summary>

新增的 `v147` 結構包含 Inactive Tabs 相關字串，但這些字串已從原本的 `InactiveTabs` 結構中移除。若這些字串已不再使用，應直接刪除而非移至新結構。請確認是否仍需要這些字串。

**判斷依據**：diff 顯示刪除原本的 `InactiveTabs` 結構，並新增 `v147` 結構包含相同內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 28519 (cache hit 28416) ｜ completion tokens 871 ｜ PR #5</sub>