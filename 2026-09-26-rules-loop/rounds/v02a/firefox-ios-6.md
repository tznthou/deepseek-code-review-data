<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async 版本，並在部分 UI 測試類別加上 @MainActor，以符合 Swift 6 的並發要求。同時修正了 NotificationManagerTests 中的斷言寫法，以及將 MockURLAuthenticationChallengeSender 標記為 final。整體改動方向正確，但需注意 async setUp/tearDown 的呼叫順序與錯誤處理，以及 @MainActor 標註的一致性。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 測試斷言從 XCTAssertTrue 改為 assert 可能導致測試失效 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26` | 閉包捕獲 center 可能造成 retain cycle | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 標註 @Sendable 可能導致不必要的限制 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:11` | setUp 改為 async 但未處理可能的錯誤 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:28` | tearDown 改為 async 但呼叫順序可能影響狀態重置 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:11` | 缺少 @MainActor 標註可能導致並發問題 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 測試斷言從 XCTAssertTrue 改為 assert 可能導致測試失效</summary>

在測試方法 `testRequestAuthorization` 中，原本使用 `XCTAssertTrue` 進行斷言，現在改為 Swift 標準庫的 `assert`。`assert` 在 Release 建置中會被編譯器移除，且 XCTest 不會將其視為測試斷言，因此此測試將永遠通過，無法驗證授權結果。應改回 `XCTAssertTrue` 或使用 `XCTAssert` 系列斷言。

**判斷依據**：diff 中將原本的 `XCTAssertTrue(granted)` 和 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(granted, ...)` 和 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26</code> 閉包捕獲 center 可能造成 retain cycle</summary>

閉包中捕獲了 `center`（可能是 `self.center` 的隱式解包），但未使用 `[weak self]` 或 `[unowned self]`。若 `center` 持有閉包，可能造成 retain cycle。建議使用 `[weak self]` 並在閉包內使用 `self?.center`。

**判斷依據**：diff 中將閉包捕獲列表改為 `[center]`，但未見 `[weak self]` 或 `[unowned self]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 標註 @Sendable 可能導致不必要的限制</summary>

`getQueuedTabs` 的 completion handler 新增了 `@Sendable` 標註，但此 handler 僅在主執行緒上被呼叫，且未跨並發域傳遞。加上 `@Sendable` 可能導致呼叫端必須使用 `@Sendable` closure，增加不必要的限制。若無跨執行緒傳遞需求，可考慮移除 `@Sendable`。

**判斷依據**：diff 中將 `completion: @escaping @MainActor ([ShareItem]) -> Void` 改為 `completion: @MainActor @Sendable @escaping ([ShareItem]) -> Void`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:11</code> setUp 改為 async 但未處理可能的錯誤</summary>

`setUp` 改為 `async throws`，但內部呼叫 `try await super.setUp()` 後未進行任何錯誤處理。若 `super.setUp()` 拋出錯誤，測試將直接失敗，可能掩蓋實際測試意圖。建議考慮是否需要在 setUp 中處理錯誤，或確保 super.setUp() 不會拋出。

**判斷依據**：diff 中將 `override func setUpWithError() throws` 改為 `override func setUp() async throws`，並在內部呼叫 `try await super.setUp()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:28</code> tearDown 改為 async 但呼叫順序可能影響狀態重置</summary>

`tearDown` 改為 `async throws`，並在最後呼叫 `try await super.tearDown()`。若 `super.tearDown()` 依賴於子類別已重置的狀態，此順序可能導致問題。建議確認 super.tearDown() 的實作是否需要在子類別清理後執行。

**判斷依據**：diff 中將 `override func tearDown()` 改為 `override func tearDown() async throws`，並將 `super.tearDown()` 移至方法開頭。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:11</code> 缺少 @MainActor 標註可能導致並發問題</summary>

此測試類別操作 UICollectionView，但未加上 `@MainActor`。雖然 setUp 和 tearDown 改為 async，但測試方法本身可能需要在主執行緒上執行。建議在類別層級加上 `@MainActor` 以確保所有 UI 操作都在主執行緒。

**判斷依據**：diff 中未見 `@MainActor` 標註，但此類別使用 UICollectionView。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10001 (cache hit 1536) ｜ completion tokens 1614 ｜ PR #6</sub>