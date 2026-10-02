<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要進行重構與可及性改進：將 pageActionStack 更名為 trailingPageActionStack、為多個 UI 容器加入 accessibilityIdentifier、修正拼字錯誤，並調整骨架畫面的約束條件。整體風險中等，最需要注意的是 updateActionStack 中可能誤將 browserActionStack 加入兩次，導致重複的 arrangedSubviews 或錯誤的動畫行為；另外，setupSkeletonAddressBarsLayout 中新增的 isLandscape 變數未被使用，且約束條件未針對橫向模式做調整，可能造成骨架畫面佈局錯誤。建議先修正這兩個問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329` | updateActionStack 中重複加入 browserActionStack | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465` | 未使用的 isLandscape 變數與未調整的約束條件 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448` | 骨架地址欄約束可能錯誤 | 0.75 |
| ⚠️ | Major | `BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419` | hasPageActions 判斷可能使用錯誤的 stack | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329</code> updateActionStack 中重複加入 browserActionStack</summary>

在 `updateActionStack` 方法中，原本應該加入 `trailingPageActionStack.arrangedSubviews`，但程式碼卻再次加入了 `browserActionStack.arrangedSubviews`，導致 `browserActionStack` 的 arrangedSubviews 被加入兩次。這會造成重複的視圖、動畫異常，甚至可能導致約束衝突。

建議修正為：
```swift
let stacks = browserActionStack.arrangedSubviews +
             navigationActionStack.arrangedSubviews +
             leadingPageActionStack.arrangedSubviews +
             trailingPageActionStack.arrangedSubviews
```

**判斷依據**：diff 中此行將原本的 `pageActionStack.arrangedSubviews` 改為 `browserActionStack.arrangedSubviews`，但前一行已經有 `browserActionStack.arrangedSubviews`，造成重複。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465</code> 未使用的 isLandscape 變數與未調整的約束條件</summary>

在 `setupSkeletonAddressBarsLayout` 中新增了 `isLandscape` 變數，但後續的約束條件並未使用它，且約束條件與原本相同，沒有針對橫向模式做任何調整。這可能表示程式碼不完整，或者該變數是多餘的。如果原本意圖是根據方向調整佈局，則需要補充對應的約束邏輯；否則應移除該變數以避免混淆。

**判斷依據**：diff 中新增了 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`，但後續的 NSLayoutConstraint.activate 區塊中完全沒有使用此變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448</code> 骨架地址欄約束可能錯誤</summary>

在 `setupSkeletonAddressBars` 中，原本的約束是 `toolbar.leadingAnchor.constraint(equalTo: leftSkeletonAddressBar.trailingAnchor)`，但被改為 `toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor)`。這可能導致 toolbar 的 leading 與 rightSkeletonAddressBar 的 trailing 對齊，而不是與 leftSkeletonAddressBar 的 trailing 對齊，造成佈局錯誤。請確認此變更是否正確，若為筆誤應改回 `leftSkeletonAddressBar`。

**判斷依據**：diff 中此行將 `leftSkeletonAddressBar` 改為 `rightSkeletonAddressBar`，但下一行仍使用 `rightSkeletonAddressBar.leadingAnchor`，可能造成衝突。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419</code> hasPageActions 判斷可能使用錯誤的 stack</summary>

在 `updateToolbarLayout` 中，原本使用 `pageActionStack.arrangedSubviews.isEmpty` 來判斷是否有頁面動作，但被改為 `leadingPageActionStack.arrangedSubviews.isEmpty`。然而，分隔線的寬度應該取決於 trailing page actions 是否存在，而不是 leading page actions。這可能導致分隔線在 trailing page actions 存在但 leading page actions 為空時被隱藏。請確認此變更是否正確，若應使用 trailing stack，請改為 `trailingPageActionStack.arrangedSubviews.isEmpty`。

**判斷依據**：diff 中此行將 `pageActionStack` 改為 `leadingPageActionStack`，但變數名稱 `hasPageActions` 暗示應包含所有頁面動作，且分隔線位於 trailing stack 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4947 (cache hit 4864) ｜ completion tokens 1333 ｜ PR #11</sub>