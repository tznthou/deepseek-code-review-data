<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 BrowserKit 套件與 ShareTo extension 遷移至 Swift 6，主要變更包括：移除 StrictConcurrency 等實驗性旗標、將測試從 async 改為同步、為靜態屬性加上 nonisolated(unsafe)、以及調整閉包的 @Sendable 標註。整體方向合理，但存在幾個需要修正的問題：MainContentBlockerGenerator.swift 移除了 MPL 授權標頭（違反 R01）；WKUIHandlerTests 中第一個測試的 expectation 被移除，可能導致測試提前結束而無法驗證非同步行為；LabelButtonHeaderView 的 wrappedAction 閉包可能造成 retain cycle。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:1` | [R01] 缺少 Mozilla Public License 標頭 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試無法驗證非同步行為 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | wrappedAction 閉包可能造成 retain cycle | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26` | 移除 async 後測試可能提前結束 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:1</code> [R01] 缺少 Mozilla Public License 標頭</summary>

此檔案原本有 MPL 2.0 授權標頭，但在此 diff 中被移除。根據規範 R01，所有 Swift 檔案必須包含 MPL 標頭。請恢復授權標頭。

**判斷依據**：diff 顯示刪除了以下三行：
- // This Source Code Form is subject to the terms of the Mozilla Public
- // License, v. 2.0. If a copy of the MPL was not distributed with this
- // file, You can obtain one at http://mozilla.org/MPL/2.0/

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureSuccess` 中，原本的 expectation 被移除，且 `wait(for:)` 也被刪除。這使得測試在呼叫 `requestMediaCapturePermission` 後立即返回，無法確保 decision handler 被呼叫並驗證其內容。若 handler 未被呼叫，測試仍會通過，失去測試意義。建議保留 expectation 並使用 `wait(for:)` 等待。

**判斷依據**：diff 顯示刪除了 `let expectation = expectation(description: ...)`、`expectation.fulfill()` 和 `wait(for: [expectation])`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> wrappedAction 閉包可能造成 retain cycle</summary>

在 `configure` 方法中，`wrappedAction` 閉包捕獲了 `moreButtonAction`，而 `moreButtonAction` 是外部傳入的閉包。若該閉包持有 self（例如呼叫者傳入的閉包捕獲了 self），則可能形成 retain cycle。建議使用 `[weak self]` 或確保閉包不會持有 self。

**判斷依據**：diff 新增了 wrappedAction 閉包，直接捕獲 moreButtonAction，未使用 weak 或 unowned。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26</code> 移除 async 後測試可能提前結束</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `await fulfillment(of:)` 等待非同步下載完成，現在改為直接呼叫下載方法後立即返回，沒有等待機制。這可能導致測試在下載完成前結束，無法驗證結果。建議保留 expectation 並使用 `wait(for:)`。

**判斷依據**：diff 顯示移除了 `let exp = expectation(description: ...)`、`exp.fulfill()` 和 `await fulfillment(of: [exp], timeout: 2.0)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7761 (cache hit 7680) ｜ completion tokens 1236 ｜ PR #10</sub>