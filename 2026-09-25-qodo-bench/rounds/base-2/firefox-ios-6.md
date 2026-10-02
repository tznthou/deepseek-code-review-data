<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個 XCTestCase 子類別的 setUp/tearDown 從同步版本遷移至 async throws 版本，並在部分測試類別加上 @MainActor 標註，以符合 Swift 6 的 concurrency 規範。整體變更方向正確，但需注意 setUp 中呼叫 super.setUp() 的順序、NotificationManagerTests 中改用 assert 可能導致測試在 release 建置中失效，以及 MockProfile 中 completion handler 的 @Sendable 標註可能造成不必要的限制。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 加上 @Sendable 可能造成不必要的限制 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16` | setUp 中呼叫 super.setUp() 的順序可能影響測試狀態 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效</summary>

在測試方法 `testRequestAuthorization` 中，原本使用 `XCTAssertTrue` 進行斷言，但此 PR 改為使用 Swift 標準函式 `assert`。`assert` 在 release 建置（`-O` 或 `-Ounchecked`）中會被編譯器移除，導致測試永遠通過，無法驗證行為。建議改回 `XCTAssertTrue` 或使用 `XCTAssert`。

**判斷依據**：diff 中將原本的 `XCTAssertTrue(granted)` 和 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(granted, ...)` 和 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 加上 @Sendable 可能造成不必要的限制</summary>

`getQueuedTabs` 的 completion handler 從 `@escaping @MainActor ([ShareItem]) -> Void` 改為 `@MainActor @Sendable @escaping ([ShareItem]) -> Void`。加上 `@Sendable` 會要求 closure 必須是 Sendable，可能導致呼叫端必須使用 `@Sendable` closure 或產生額外的 concurrency 檢查。若此 API 僅在測試中使用，且不需要跨 actor 傳遞，建議移除 `@Sendable` 以避免不必要的限制。

**判斷依據**：diff 中將原本的 `@escaping @MainActor ([ShareItem]) -> Void` 改為 `@MainActor @Sendable @escaping ([ShareItem]) -> Void`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16</code> setUp 中呼叫 super.setUp() 的順序可能影響測試狀態</summary>

在 `StoriesFeedDiffableDataSourceTests` 的 `setUp` 中，原本先呼叫 `super.setUpWithError()` 再進行設定，現在改為先呼叫 `try await super.setUp()` 再進行設定。若 `super.setUp()` 會重置某些狀態，可能影響後續設定。建議確認 `XCTestCase` 的 `setUp` 是否會影響測試環境，或考慮將 `super.setUp()` 放在設定之後。

**判斷依據**：diff 中顯示原本的 `setUpWithError` 先呼叫 `super.setUpWithError()`，而新的 `setUp` 也是先呼叫 `super.setUp()`，但其他測試類別（如 `SyncContentSettingsViewControllerTests`）也是先呼叫 `super.setUp()`，因此可能不是問題。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7942 (cache hit 7936) ｜ completion tokens 1042 ｜ PR #6</sub>