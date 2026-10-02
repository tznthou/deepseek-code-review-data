<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async 版本，並為部分 UI 相關測試類別加上 @MainActor 標註，以符合 Swift 6 的 concurrency 要求。同時調整了 Mock 類別的 Sendable 遵從與 final 修飾。整體改動方向正確，但需注意 async setUp/tearDown 的執行順序與例外處理，以及 @MainActor 標註是否完整涵蓋所有 UI 操作。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 測試斷言從 XCTAssertTrue 改為 assert 可能導致測試失效 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:28` | 測試斷言從 XCTAssertTrue 改為 assert 可能導致測試失效 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 標註 @Sendable 可能造成不必要的限制 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9` | MockUserNotificationCenter 標註 @unchecked Sendable 可能隱藏執行緒安全問題 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11` | 移除 @MainActor 可能導致測試在背景執行緒執行 UI 操作 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 測試斷言從 XCTAssertTrue 改為 assert 可能導致測試失效</summary>

在 `testRequestAuthorization` 中，原本使用 `XCTAssertTrue` 進行斷言，現在改為 Swift 標準庫的 `assert`。`assert` 在 release 建置中會被編譯器移除，且 XCTest 不會將其視為測試失敗，因此此測試將永遠通過，失去驗證功能。建議改回 `XCTAssertTrue` 或使用 `XCTAssert`。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，且 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:28</code> 測試斷言從 XCTAssertTrue 改為 assert 可能導致測試失效</summary>

同前，第二個斷言也改為 `assert`，同樣會導致測試在 release 模式下失效。建議改回 `XCTAssertTrue`。

**判斷依據**：diff 中將 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 標註 @Sendable 可能造成不必要的限制</summary>

`getQueuedTabs` 的 completion handler 新增了 `@Sendable` 標註。若呼叫端傳入的 closure 捕獲非 Sendable 的狀態，可能導致編譯錯誤。請確認所有呼叫端都能滿足此要求，或考慮移除 `@Sendable` 以維持彈性。

**判斷依據**：diff 中將 `completion: @escaping @MainActor ([ShareItem]) -> Void` 改為 `completion: @MainActor @Sendable @escaping ([ShareItem]) -> Void`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9</code> MockUserNotificationCenter 標註 @unchecked Sendable 可能隱藏執行緒安全問題</summary>

將 `MockUserNotificationCenter` 標註為 `@unchecked Sendable` 表示開發者自行保證其執行緒安全，但此類別包含可變狀態（如 `pendingRequests`、`getSettingsWasCalled` 等），若在多執行緒環境下使用可能導致資料競爭。建議改用 actor 或鎖保護，或確認此 Mock 僅在單一執行緒使用。

**判斷依據**：diff 中新增 `@unchecked Sendable` 遵從。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11</code> 移除 @MainActor 可能導致測試在背景執行緒執行 UI 操作</summary>

原本 `EditBookmarkViewModelTests` 有 `@MainActor` 標註，現在被移除。若測試中涉及 UI 相關操作（例如建立 UITableView 或呼叫 UI API），可能導致執行緒安全問題。請確認此測試類別是否真的不需要 @MainActor，或考慮保留。

**判斷依據**：diff 中移除了 `@MainActor` 標註。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8789 (cache hit 7936) ｜ completion tokens 1279 ｜ PR #6</sub>