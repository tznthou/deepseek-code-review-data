<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 是 Swift 6 遷移的一部分，主要將測試類別的 setUp/tearDown 改為 async 版本、為部分 UI 測試類別加上 @MainActor、調整 mock 類別的 Sendable 遵從，並將 NotificationManagerTests 中的 XCTAssert 改為 assert。整體改動符合 Swift 6 的 concurrency 要求，但需注意 setUp/tearDown 的呼叫順序、@MainActor 的套用一致性，以及 assert 在測試中的適用性。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 測試中使用 assert 可能導致測試永遠通過 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11` | 移除 @MainActor 可能導致測試在非主執行緒執行 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:11` | setUp 中呼叫 super.setUp() 的順序可能影響測試狀態 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:28` | tearDown 中呼叫 super.tearDown() 的順序可能影響資源釋放 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 標註 @Sendable 可能造成不必要的限制 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9` | Mock 類別加上 @unchecked Sendable 可能隱藏執行緒安全問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 測試中使用 assert 可能導致測試永遠通過</summary>

在測試方法 `testRequestAuthorization` 中，原本使用 `XCTAssertTrue` 進行斷言，現在改為 Swift 標準庫的 `assert`。`assert` 在 debug 模式下才會觸發，但在 release 模式下會被編譯器移除，且 XCTest 測試通常以 debug 模式執行，但若測試配置為 release 或使用優化，斷言將不會執行，導致測試失去驗證效果。此外，`assert` 失敗時會直接 crash 而不是記錄測試失敗，這會使測試結果難以診斷。建議改回使用 XCTest 的斷言（如 `XCTAssertTrue`），或使用 `XCTAssert` 系列函數。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，並將 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11</code> 移除 @MainActor 可能導致測試在非主執行緒執行</summary>

原本類別上有 `@MainActor`，但在此 PR 中被移除。若此測試類別中的屬性或方法需要在主執行緒上執行（例如涉及 UI 或 main actor 隔離的程式碼），移除後可能導致測試在背景執行緒執行，進而產生 concurrency 錯誤或非預期行為。請確認此類別是否真的不需要 main actor 隔離，若需要則應保留。

**判斷依據**：diff 中刪除了 `@MainActor` 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:11</code> setUp 中呼叫 super.setUp() 的順序可能影響測試狀態</summary>

在 async setUp 中，先呼叫 `try await super.setUp()` 再進行其他設定。若 super.setUp() 中有重置狀態或非同步操作，可能影響後續設定。建議確認 super.setUp() 的行為，並考慮是否應在設定完成後再呼叫 super.setUp()，或保持原有順序。

**判斷依據**：diff 中將原本的 `try super.setUpWithError()` 改為 `try await super.setUp()`，並置於設定之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:28</code> tearDown 中呼叫 super.tearDown() 的順序可能影響資源釋放</summary>

在 async tearDown 中，先執行清理動作（如將屬性設為 nil），最後才呼叫 `try await super.tearDown()`。若 super.tearDown() 依賴於子類別的狀態，可能導致問題。建議確認 super.tearDown() 的行為，並考慮是否應先呼叫 super.tearDown() 再進行清理。

**判斷依據**：diff 中將 `super.tearDown()` 移至方法開頭，並改為 async 版本。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 標註 @Sendable 可能造成不必要的限制</summary>

將 `getQueuedTabs` 的 completion handler 加上 `@Sendable`，這表示該 closure 必須是 Sendable。若呼叫端傳入的 closure 捕獲了非 Sendable 的狀態，將導致編譯錯誤。請確認所有呼叫端都能滿足此要求，否則可能需要調整設計。

**判斷依據**：diff 中將 `@escaping @MainActor` 改為 `@MainActor @Sendable @escaping`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9</code> Mock 類別加上 @unchecked Sendable 可能隱藏執行緒安全問題</summary>

將 `MockUserNotificationCenter` 加上 `@unchecked Sendable`，這表示編譯器不會檢查其內部狀態的執行緒安全性。若此 mock 在多執行緒環境下被使用，可能導致資料競爭。請確認此 mock 僅在測試中使用且不會跨執行緒共享，否則應考慮實作適當的同步機制。

**判斷依據**：diff 中新增 `@unchecked Sendable`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7906 (cache hit 7808) ｜ completion tokens 1645 ｜ PR #6</sub>