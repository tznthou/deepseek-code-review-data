<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 主要為 UI 元件新增 accessibility identifier、重新命名變數以修正拼字、調整 skeleton 佈局邏輯，並修正一個約束條件。整體改動符合多項 repo 規範，但發現兩處違反 R13（UI 常數未集中於 UX struct）及一處違反 R09（UI 程式碼缺少 @MainActor 標註）。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:471` | [R13] UI 常數應定義於 UX struct 中 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:476` | [R13] UI 常數應定義於 UX struct 中 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:461` | [R09] UI 程式碼應標註 @MainActor | 0.80 |

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:471</code> [R13] UI 常數應定義於 UX struct 中</summary>

在 `setupSkeletonAddressBarsLayout()` 中直接使用了 `UX.skeletonBarWidthOffset`，但該常數未定義於 `AddressToolbarContainer` 的巢狀 `UX` struct 內，而是散落在程式碼中。根據 R13，所有 UI 常數應集中於巢狀 `UX` struct。建議將 `skeletonBarWidthOffset` 移至 `AddressToolbarContainer` 的 `UX` struct 中，並以 `UX.skeletonBarWidthOffset` 引用。

**判斷依據**：diff 中新增的約束條件使用了 `UX.skeletonBarWidthOffset`，但該常數未在 `AddressToolbarContainer` 的 `UX` struct 中定義（可從檔案其他部分確認）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:476</code> [R13] UI 常數應定義於 UX struct 中</summary>

在 `setupSkeletonAddressBarsLayout()` 中直接使用了 `UX.skeletonBarWidthOffset`，但該常數未定義於 `AddressToolbarContainer` 的巢狀 `UX` struct 內。根據 R13，所有 UI 常數應集中於巢狀 `UX` struct。建議將 `skeletonBarWidthOffset` 移至 `AddressToolbarContainer` 的 `UX` struct 中，並以 `UX.skeletonBarWidthOffset` 引用。

**判斷依據**：diff 中新增的約束條件使用了 `UX.skeletonBarWidthOffset`，但該常數未在 `AddressToolbarContainer` 的 `UX` struct 中定義（可從檔案其他部分確認）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:461</code> [R09] UI 程式碼應標註 @MainActor</summary>

`setupSkeletonAddressBarsLayout()` 直接操作 UIKit 約束條件，但未標註 `@MainActor`。根據 R09，所有 UI 相關程式碼應標註 `@MainActor` 以確保執行於主執行緒。建議在方法或類別層級加上 `@MainActor`。

**判斷依據**：diff 中新增的 `setupSkeletonAddressBarsLayout()` 方法未標註 `@MainActor`，且其內容包含 UIKit 約束條件操作。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7043 (cache hit 7040) ｜ completion tokens 894 ｜ PR #11</sub>