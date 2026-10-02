<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個 XCTestCase 子類別的 setUp/tearDown 改為 async 版本，並在部分 UI 相關測試類別加上 @MainActor，以符合 Swift 6 的 concurrency 要求。整體變更方向正確，但有一處測試斷言從 XCTAssertTrue 改為 assert，可能導致測試在 release 建置中失效；另外部分類別未加上 @MainActor，可能仍會觸發 main actor isolation 警告。建議修正 NotificationManagerTests 的斷言方式，並全面檢查需要 @MainActor 的測試類別。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14` | 測試類別可能缺少 @MainActor 標註 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效</summary>

在測試方法 `testRequestAuthorization` 中，原本的 `XCTAssertTrue` 被改為 Swift 標準庫的 `assert`。`assert` 在 release 建置（`-O`）中會被編譯器移除，因此測試將不會驗證任何條件，可能導致測試永遠通過而失去防護力。建議改回 `XCTAssertTrue` 或使用 `XCTAssert` 系列斷言。

**判斷依據**：diff 中將原本的 `XCTAssertTrue(granted)` 和 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(granted, ...)` 和 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14</code> 測試類別可能缺少 @MainActor 標註</summary>

此測試類別涉及 UI 相關的 ViewModel，但未加上 `@MainActor`。在 Swift 6 嚴格 concurrency 下，若 ViewModel 或相關 API 被標註為 `@MainActor`，此測試類別可能仍會產生 isolation 警告。建議確認是否需要加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他 UI 相關測試類別（如 StoriesFeedDiffableDataSourceTests）已加上。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7942 (cache hit 7936) ｜ completion tokens 658 ｜ PR #6</sub>