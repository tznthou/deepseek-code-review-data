<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

本次 PR 主要為 UI 元件新增 accessibility identifier、修正變數拼字、調整 Auto Layout 約束，並重構 skeleton address bar 的佈局設定。主要風險在於 skeleton address bar 的約束變更可能導致佈局錯誤，以及新增的 accessibility identifier 未使用 ViewModel 設定，違反專案規範。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Views/BrowserViewController.swift:138` | [R07] UI 元件應使用 ViewModel 設定 accessibility identifier | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448` | Skeleton address bar 約束變更可能導致佈局錯誤 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465` | [R13] 使用 UIApplication.shared.statusBarOrientation 判斷橫向模式 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Views/BrowserViewController.swift:138</code> [R07] UI 元件應使用 ViewModel 設定 accessibility identifier</summary>

新增的 accessibility identifier 直接以字串常數指派，未透過 ViewModel 傳入。專案規範 R07 要求 UI 元件應透過 ViewModel struct 封裝設定，以維持關注點分離與可測試性。建議將這些 identifier 移至對應的 ViewModel 中，並在 configure 方法中設定。

**判斷依據**：diff 中多處直接指派 accessibilityIdentifier，例如 statusBarOverlay、header、overKeyboardContainer 等，均未使用 ViewModel。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448</code> Skeleton address bar 約束變更可能導致佈局錯誤</summary>

原本 toolbar.leadingAnchor 是連到 leftSkeletonAddressBar.trailingAnchor，現在改為連到 rightSkeletonAddressBar.trailingAnchor，這可能造成 toolbar 與 skeleton bar 重疊或位置錯誤。請確認此變更是否為預期行為，並檢查相關約束是否正確。

**判斷依據**：diff 中將 leftSkeletonAddressBar 改為 rightSkeletonAddressBar，但未同步調整其他約束，可能導致衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465</code> [R13] 使用 UIApplication.shared.statusBarOrientation 判斷橫向模式</summary>

使用 UIApplication.shared.statusBarOrientation 來判斷是否為橫向模式，但此 API 在 iOS 13 後已不建議使用，且可能無法反映實際介面方向。建議改用 view 的 trait collection 或 window 的 interface orientation。

**判斷依據**：diff 中新增此行程式碼，但未使用更現代的方式取得方向。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7043 (cache hit 6912) ｜ completion tokens 734 ｜ PR #11</sub>