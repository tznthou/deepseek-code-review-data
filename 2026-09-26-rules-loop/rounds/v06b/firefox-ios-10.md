<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、將測試改為同步、加入 @Sendable 標註，以及將 ShareTo 的 SWIFT_VERSION 設為 6.0。整體方向合理，但需注意測試同步化可能導致非同步回呼未被等待而漏測，以及移除 @MainActor 後 GCDWebServer 初始化可能回到背景執行緒造成崩潰。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26` | 測試改為同步後，非同步回呼可能未被等待 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒 | 0.75 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試未驗證決策處理器呼叫 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | wrappedAction 可能造成不必要的閉包包裝 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26</code> 測試改為同步後，非同步回呼可能未被等待</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `await fulfillment(of: [exp], timeout: 2.0)` 等待非同步下載完成，現在移除了 expectation 與等待，直接呼叫 `siteDownloader.downloadImage` 後測試方法即結束。若 `downloadImage` 是非同步執行，測試可能在回呼執行前就返回，導致斷言從未執行，測試失去驗證效果。建議保留 expectation 並使用 `wait(for:timeout:)` 等待，或將測試方法改為 async 並 await 完成。

**判斷依據**：diff 中移除了 `let exp = expectation(description: "Image download and parse")` 與 `await fulfillment(of: [exp], timeout: 2.0)`，且回呼內不再呼叫 `exp.fulfill()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒</summary>

原本 `startMockImageServer` 標註 `@MainActor` 並有註解說明 GCDWebServer 必須在主執行緒初始化，否則測試單獨執行時會崩潰。現在移除了 `@MainActor`，且呼叫端也改為同步，若測試方法本身未在主執行緒執行（例如 XCTest 的非同步測試），可能導致 GCDWebServer 初始化於背景執行緒而崩潰。建議保留 `@MainActor` 或確保測試方法在主執行緒執行。

**判斷依據**：diff 中移除了 `@MainActor` 標註與相關註解，且呼叫端改為 `try? startMockImageServer(...)` 同步呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試未驗證決策處理器呼叫</summary>

在 `testRequestMediaCaptureSuccess` 中，原本使用 expectation 等待決策處理器被呼叫，現在移除了 expectation 與 `wait(for:)`，僅在回呼內執行斷言。若 `requestMediaCapturePermission` 是非同步呼叫，測試可能在回呼執行前就結束，導致斷言未執行。建議保留 expectation 或改用 async 測試。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 與 `wait(for: [expectation])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> wrappedAction 可能造成不必要的閉包包裝</summary>

新增的 `wrappedAction` 閉包僅呼叫 `moreButtonAction?(button)`，沒有額外邏輯，可能只是為了滿足型別需求。若 `ActionButtonViewModel` 的 `touchUpAction` 已接受 `@Sendable @MainActor` 閉包，則可直接傳遞 `moreButtonAction`，無需包裝。建議確認型別需求，若可簡化則移除包裝。

**判斷依據**：diff 中新增了 wrappedAction 閉包，並將其傳遞給 ActionButtonViewModel。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8963 (cache hit 8960) ｜ completion tokens 1204 ｜ PR #10</sub>