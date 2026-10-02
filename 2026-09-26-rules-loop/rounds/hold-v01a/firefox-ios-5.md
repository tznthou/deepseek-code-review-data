<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除 Inactive Tabs 功能，包含刪除相關檔案、清理狀態與動作、更新測試與 UI 測試。主要風險在於 TabsPanelState.swift 中 scrollToTab 的索引計算可能 off-by-one，以及 Strings.swift 中新增的 v147 結構體可能造成重複定義或未使用。整體移除乾淨，但需確認上述問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143` | scrollToTab 的索引計算可能 off-by-one | 0.80 |
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:8461` | 新增的 v147 結構體可能造成重複定義或未使用 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172` | scrollToTab 使用硬編碼 section 1 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143</code> scrollToTab 的索引計算可能 off-by-one</summary>

在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，原本回傳 `state.tabs.count - 1`，但修改後變成 `state.tabs.count`。這可能導致滾動到超出最後一個項目的位置，造成越界或滾動失敗。

建議改回 `state.tabs.count - 1`，或確認 collection view 的 section 數量與 item 數量後再決定。

**判斷依據**：diff 中此行由 `state.tabs.count - 1` 改為 `state.tabs.count`，且上下文顯示此為無選取 tab 時的 fallback。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:8461</code> 新增的 v147 結構體可能造成重複定義或未使用</summary>

原本的 `InactiveTabs` 結構體被刪除，但新增了一個 `v147` 結構體，內容完全相同。這可能導致：
1. 若 `v147` 未被使用，則為無效程式碼。
2. 若其他程式碼仍引用舊的 `InactiveTabs`，則會編譯錯誤。

請確認是否應直接刪除這些字串，或保留但更新引用。

**判斷依據**：diff 顯示刪除了 `InactiveTabs` 結構體，並在 `v147` 中重新定義相同內容。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172</code> scrollToTab 使用硬編碼 section 1</summary>

在 `scrollToTab` 方法中，原本根據 `scrollState.isInactiveTabSection` 決定 section，現在固定為 1。由於移除 inactive tabs 後只剩一個 section，這樣做可能正確，但若未來新增 section 則容易出錯。建議使用常數或從 snapshot 取得 section index。

**判斷依據**：diff 中此行由動態 section 改為固定 1。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 28482 (cache hit 26368) ｜ completion tokens 800 ｜ PR #5</sub>