<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要重構 BrowserAddressToolbar 的 pageActionStack 命名、修正拼字錯誤、新增多個 accessibility identifier，並調整 skeleton address bar 的約束。整體風險中等：命名重構看似一致，但有一處疑似誤改（updateActionStack 的 stacks 合併），可能導致動畫或可視性更新遺漏；skeleton 約束的變更需確認與既有邏輯一致。建議優先修正該誤改並補齊測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329` | updateActionStack 的 stacks 合併誤將 pageActionStack 改為 browserActionStack | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448` | skeleton address bar 的 leading 約束可能誤接至 rightSkeletonAddressBar | 0.80 |
| ⚠️ | Major | `BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419` | hasPageActions 判斷誤用 leadingPageActionStack | 0.75 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465` | 使用已棄用的 statusBarOrientation API | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329</code> updateActionStack 的 stacks 合併誤將 pageActionStack 改為 browserActionStack</summary>

在 `updateActionStack` 方法中，原本合併 `browserActionStack`、`navigationActionStack`、`leadingPageActionStack`、`pageActionStack` 的 arrangedSubviews，但此 PR 將最後一項改為 `browserActionStack`，導致 `trailingPageActionStack`（原 `pageActionStack`）的 arrangedSubviews 未被納入。這會使後續的動畫或可視性更新遺漏 trailing page actions，可能造成 UI 不一致或動畫失效。

建議改回 `trailingPageActionStack.arrangedSubviews`。

**判斷依據**：diff 中第 329-332 行顯示最後一項由 `pageActionStack.arrangedSubviews` 改為 `browserActionStack.arrangedSubviews`，但根據上下文，此處應為 `trailingPageActionStack`（原 `pageActionStack`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448</code> skeleton address bar 的 leading 約束可能誤接至 rightSkeletonAddressBar</summary>

在 `setupSkeletonAddressBarsLayout` 中，原本 `toolbar.leadingAnchor.constraint(equalTo: leftSkeletonAddressBar.trailingAnchor)` 被改為 `toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor)`。這可能導致 toolbar 的 leading 錯誤地對齊到右側 skeleton bar 的 trailing，造成佈局錯亂。

請確認此變更是否為預期；若非預期，應改回 `leftSkeletonAddressBar.trailingAnchor`。

**判斷依據**：diff 中第 448 行顯示 leading 約束的對象由 `leftSkeletonAddressBar` 改為 `rightSkeletonAddressBar`，但 trailing 約束仍為 `rightSkeletonAddressBar.leadingAnchor`，可能造成衝突。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419</code> hasPageActions 判斷誤用 leadingPageActionStack</summary>

在 `updateToolbarLayout` 中，原本 `let hasPageActions = !pageActionStack.arrangedSubviews.isEmpty` 被改為 `!leadingPageActionStack.arrangedSubviews.isEmpty`。但此處的 `hasPageActions` 應代表 trailing page actions 是否存在，以決定 divider 寬度。若 leading 和 trailing page actions 不同時存在，可能導致 divider 顯示錯誤。

建議改回 `!trailingPageActionStack.arrangedSubviews.isEmpty`。

**判斷依據**：diff 中第 419 行顯示判斷對象由 `pageActionStack` 改為 `leadingPageActionStack`，但變數名稱 `hasPageActions` 及後續 divider 設定應與 trailing page actions 相關。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465</code> 使用已棄用的 statusBarOrientation API</summary>

新增的 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape` 使用了 iOS 13 已棄用的 `statusBarOrientation`，可能導致未來版本無法正確取得方向。建議改用 `view.window?.windowScene?.interfaceOrientation` 或其他現代 API。

**判斷依據**：diff 中新增此行程式碼，但未見後續使用，且該 API 已棄用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4947 (cache hit 1536) ｜ completion tokens 1259 ｜ PR #11</sub>