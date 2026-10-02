<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試類別遷移至 Swift 6 的 async setUp/tearDown 模式，並加上 @MainActor 標註。整體變更集中於測試程式碼，風險較低。主要問題在於 NotificationManagerTests 中將 XCTAssertTrue 改為 assert，可能導致測試在 release 建置中被跳過；另外部分測試類別未加上 @MainActor，可能導致 Swift 6 的併發檢查警告。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中被跳過 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26` | 測試方法未標註 @MainActor，但使用非 Sendable 的 center 屬性 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | getQueuedTabs 的 completion handler 標註 @MainActor 但未在實作中確保呼叫於主執行緒 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11` | 移除 @MainActor 可能導致測試在非主執行緒執行 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中被跳過</summary>

在 `testRequestAuthorization` 中，原本的 `XCTAssertTrue` 被改為 `assert`。`assert` 在 release 建置中會被編譯器移除，導致測試失去驗證功能。建議改回 `XCTAssertTrue` 或使用 `XCTAssert`。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，且 `assert` 在 Swift 中僅在 debug 模式有效。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26</code> 測試方法未標註 @MainActor，但使用非 Sendable 的 center 屬性</summary>

`testRequestAuthorization` 方法未標註 `@MainActor`，但 closure 中捕捉了 `center`（MockUserNotificationCenter 已標註為 @unchecked Sendable）。雖然 @unchecked Sendable 可暫時規避編譯器檢查，但若測試在非主執行緒執行，可能導致資料競爭。建議將測試方法標註為 @MainActor，或確保所有存取都在主執行緒。

**判斷依據**：diff 中將 closure 改為捕捉 `[center]`，但方法本身沒有 @MainActor 標註。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> getQueuedTabs 的 completion handler 標註 @MainActor 但未在實作中確保呼叫於主執行緒</summary>

`getQueuedTabs` 的 completion handler 被標註為 `@MainActor @Sendable @escaping`，但實作中透過 `Task { @MainActor in ... }` 呼叫，理論上正確。然而，`getQueuedTabsCalled` 的遞增也在該 Task 內，若測試未等待 Task 完成，可能導致計數不正確。建議確認測試中是否有適當的等待機制。

**判斷依據**：diff 中修改了 completion 的標註，但未看到對應的測試變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11</code> 移除 @MainActor 可能導致測試在非主執行緒執行</summary>

原本類別標註為 `@MainActor`，但此次 diff 移除了該標註。若測試方法涉及 UI 或非執行緒安全的屬性，可能導致不穩定。建議確認是否真的需要移除，或改為在個別方法上標註。

**判斷依據**：diff 中刪除了 `@MainActor` 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 26390 (cache hit 1536) ｜ completion tokens 1059 ｜ PR #6</sub>