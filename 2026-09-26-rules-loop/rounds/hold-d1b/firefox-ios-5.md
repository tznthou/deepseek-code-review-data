<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除 Inactive Tabs 功能，包含刪除相關檔案、調整狀態與 UI 程式碼，並更新測試。主要風險在於刪除功能後可能遺留未清理的程式碼或違反專案規範。最需優先確認的是 TabPanelAction.swift 中移除 MPL 授權標頭是否違反 R01，以及 TabsPanelState.swift 中 scrollToTab 的索引計算是否正確。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Tabs/Action/TabPanelAction.swift:1` | [R01] 移除 MPL 授權標頭 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | scrollToTab 索引計算可能錯誤 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172` | 硬編碼 section 索引 | 0.70 |
| 🔸 | Minor | `firefox-ios/Shared/Strings.swift:8461` | 新增 v147 struct 但未使用 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/Action/TabPanelAction.swift:1</code> [R01] 移除 MPL 授權標頭</summary>

此檔案原本有 Mozilla Public License 標頭，但在此 PR 中被移除。根據規範 R01，所有 Swift 檔案必須包含 MPL 標頭。請確認是否為意外移除，並恢復標頭。

**判斷依據**：diff 顯示刪除了以下三行：
- // This Source Code Form is subject to the terms of the Mozilla Public
- // License, v. 2.0. If a copy of the MPL was not distributed with this
- // file, You can obtain one at http://mozilla.org/MPL/2.0/

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> scrollToTab 索引計算可能錯誤</summary>

在 `createTabScrollBehavior` 中，當找不到選取的 tab 且 tabs 不為空時，原本回傳 `state.tabs.count - 1`，但修改後變成 `state.tabs.count`。這可能導致索引超出範圍，因為陣列索引是從 0 開始。請確認此變更是否正確，或應維持 `count - 1`。

**判斷依據**：diff 顯示：
-                return ScrollState(toIndex: state.tabs.count - 1, isInactiveTabSection: false, withAnimation: shouldAnimate)
+                return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172</code> 硬編碼 section 索引</summary>

在 `scrollToTab` 中，section 索引被硬編碼為 1。由於移除了 inactive tabs section，現在只有一個 section，索引應為 0。請確認此處是否應改為 0，或使用更明確的方式取得 section 索引。

**判斷依據**：diff 顯示：
-        let section: Int = scrollState.isInactiveTabSection ? 0 : 1
-        let indexPath = IndexPath(row: scrollState.toIndex, section: section)
+        let indexPath = IndexPath(row: scrollState.toIndex, section: 1)

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 新增 v147 struct 但未使用</summary>

新增了 `struct v147` 並包含 Inactive Tabs 相關字串，但這些字串似乎已不再使用（因為功能已移除）。請確認是否應一併刪除，或保留以供未來使用。

**判斷依據**：diff 顯示新增了整個 v147 struct，包含多個 Inactive Tabs 相關的 MZLocalizedString。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 28519 (cache hit 28416) ｜ completion tokens 989 ｜ PR #5</sub>