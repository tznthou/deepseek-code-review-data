<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo extension 遷移至 Swift 6，主要變更包括：移除 StrictConcurrency 等實驗性旗標、將測試從 async 改為同步並使用 wait(for:)、為閉包加上 @Sendable 標註、以及將 ContentBlockerGenerator 標記為 nonisolated(unsafe)。整體風險中等，主要疑慮在於移除 StrictConcurrency 後可能隱藏資料隔離問題，以及測試中移除 expectation 可能導致測試提前結束而漏測非同步行為。建議確認這些變更不會引入新的併發錯誤。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏資料競爭 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12` | 移除 expectation 可能導致測試提前結束 | 0.75 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:35` | 移除 expectation 可能導致測試提前結束 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | 閉包包裝可能造成不必要的 @MainActor 隔離 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏資料競爭</summary>

將 `generator` 標記為 `nonisolated(unsafe)` 表示開發者手動保證其執行緒安全，但註解中明確指出 `ContentBlockerGenerator` 並非執行緒安全。若此靜態屬性被多個執行緒同時存取，可能導致資料競爭或未定義行為。建議確認 `ContentBlockerGenerator.factory()` 的回傳值是否真的不可變且內部狀態安全，或考慮使用鎖定、actor 或其他同步機制。

**判斷依據**：diff 中新增了 `nonisolated(unsafe)` 修飾詞，且上方註解寫著 `// FXIOS-14548 ContentBlockerGenerator is not thread safe`，顯示開發者已知其非執行緒安全，但選擇用 unsafe 標記來繞過編譯器檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12</code> 移除 expectation 可能導致測試提前結束</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `expectation` 等待非同步下載完成，但修改後移除了 `expectation` 的建立與等待，且未使用 `wait(for:)`。這可能導致測試方法在非同步回呼執行前就返回，使得測試永遠通過，無法驗證實際行為。建議保留 expectation 或改用 `wait(for:)` 來等待非同步操作。

**判斷依據**：diff 中刪除了 `let exp = expectation(description: "Image download and parse")` 以及 `await fulfillment(of: [exp], timeout: 2.0)`，且未加入 `wait(for:)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:35</code> 移除 expectation 可能導致測試提前結束</summary>

在 `testRequestMediaCaptureSuccess` 中，原本使用 `expectation` 等待 decision handler 被呼叫，但修改後移除了 expectation 的建立與等待，且未使用 `wait(for:)`。這可能導致測試方法在非同步回呼執行前就返回，使得測試永遠通過，無法驗證實際行為。建議保留 expectation 或改用 `wait(for:)` 來等待非同步操作。

**判斷依據**：diff 中刪除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 以及 `wait(for: [expectation])`，且未加入其他等待機制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> 閉包包裝可能造成不必要的 @MainActor 隔離</summary>

在 `configure` 方法中，新增了一個 `wrappedAction` 閉包來呼叫 `moreButtonAction`，並將其傳遞給 `ActionButtonViewModel`。此包裝可能只是為了滿足型別檢查，但若 `moreButtonAction` 本身已是 `@MainActor`，此包裝可能導致額外的隔離或效能影響。建議確認是否可以直接傳遞 `moreButtonAction`，或簡化此處的型別轉換。

**判斷依據**：diff 中新增了 `wrappedAction` 閉包，並將其指派給 `touchUpAction`，而原本的 `moreButtonAction` 參數型別已改為 `(@Sendable @MainActor (UIButton) -> Void)?`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10279 (cache hit 1536) ｜ completion tokens 1549 ｜ PR #10</sub>