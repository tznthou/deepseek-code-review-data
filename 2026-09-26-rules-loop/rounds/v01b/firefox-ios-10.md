<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、將測試改為同步、加入 @Sendable 標註，以及設定 SWIFT_VERSION = 6.0。整體方向合理，但需注意：移除 @MainActor 於 startMockImageServer 可能導致 GCDWebServer 初始化於背景執行緒而崩潰；移除測試中的 expectation 可能造成測試提前結束而未驗證結果；移除 MPL 標頭違反專案規範。建議優先修正上述問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒而崩潰 | 0.90 |
| ⚠️ | Major | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:1` | [R01] 移除 MPL 標頭違反專案規範 | 0.90 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27` | 移除 expectation 可能導致測試提前結束而未驗證結果 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | 移除 expectation 可能導致測試未等待非同步呼叫 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒而崩潰</summary>

原本的註解明確指出 GCDWebServer 必須在主執行緒初始化，否則測試單獨執行時會崩潰。移除 @MainActor 後，startMockImageServer 可能從背景執行緒呼叫，導致崩潰。建議保留 @MainActor 或確保呼叫端在主執行緒。

**判斷依據**：diff 中移除了 @MainActor 與相關註解，且測試方法已改為同步，可能從非主執行緒呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:1</code> [R01] 移除 MPL 標頭違反專案規範</summary>

此檔案移除了 Mozilla Public License 標頭，違反專案規範 R01。請保留標頭。

**判斷依據**：diff 中刪除了 MPL 標頭。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27</code> 移除 expectation 可能導致測試提前結束而未驗證結果</summary>

在 testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase 中，原本使用 expectation 等待非同步下載完成，但移除後測試方法立即返回，下載結果可能未被驗證。建議保留 expectation 或改用 async/await。

**判斷依據**：diff 中移除了 expectation 的建立與 fulfillment，且測試方法改為同步。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> 移除 expectation 可能導致測試未等待非同步呼叫</summary>

在 testRequestMediaCaptureSuccess 中，原本使用 expectation 等待 decisionHandler 被呼叫，但移除後測試可能提前結束。建議保留 expectation 或改用 async/await。

**判斷依據**：diff 中移除了 expectation 的建立與 wait。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8973 (cache hit 8960) ｜ completion tokens 859 ｜ PR #10</sub>