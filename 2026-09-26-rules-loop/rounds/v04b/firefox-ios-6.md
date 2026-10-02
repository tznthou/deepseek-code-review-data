<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Swift 6 遷移的一部分，主要將測試類別的 setUp/tearDown 改為 async 版本、為 UI 相關測試類別加上 @MainActor、調整 mock 類別的 Sendable 遵從，並將部分 XCTAssert 改為 assert。整體方向正確，但需注意：NotificationManagerTests 中將 XCTAssert 改為 assert 可能導致測試在 release 建置中失效；部分測試類別未加上 @MainActor（如 SyncContentSettingsViewControllerTests、FxAWebViewModelTests 等）可能仍有 Swift 6 的 concurrency 警告；MockUserNotificationCenter 標記為 @unchecked Sendable 可能隱藏執行緒安全問題。建議修正上述問題後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssert 可能導致測試在 release 建置中失效 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:15` | [R09] 測試類別未標註 @MainActor，可能仍有 Swift 6 concurrency 警告 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14` | [R09] 測試類別未標註 @MainActor，可能仍有 Swift 6 concurrency 警告 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9` | 使用 @unchecked Sendable 可能隱藏執行緒安全問題 | 0.50 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 標註 @Sendable 可能造成不必要的限制 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssert 可能導致測試在 release 建置中失效</summary>

在測試方法 `testRequestAuthorization` 中，原本的 `XCTAssertTrue` 被改為 `assert`。`assert` 在 release 建置（`-O`）中會被編譯器移除，因此若測試套件以 release 模式執行，這些斷言將不會被執行，導致測試失去驗證效果。建議改回 `XCTAssertTrue` 或使用 `XCTAssert` 系列方法。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，且 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:15</code> [R09] 測試類別未標註 @MainActor，可能仍有 Swift 6 concurrency 警告</summary>

此測試類別涉及 UIViewController（SyncContentSettingsViewController），但未加上 `@MainActor`。在 Swift 6 嚴格 concurrency 模式下，若該類別或其使用的 API 要求主執行緒，可能會產生編譯警告或錯誤。建議確認是否需要加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他 UI 相關測試類別（如 StoriesFeedDiffableDataSourceTests）已加上。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14</code> [R09] 測試類別未標註 @MainActor，可能仍有 Swift 6 concurrency 警告</summary>

此測試類別涉及 FxAWebViewModel，可能包含 UI 相關邏輯，但未加上 `@MainActor`。建議確認是否需要加上 `@MainActor` 以符合規範。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他 UI 相關測試類別已加上。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockUserNotificationCenter.swift:9</code> 使用 @unchecked Sendable 可能隱藏執行緒安全問題</summary>

`MockUserNotificationCenter` 被標記為 `@unchecked Sendable`，這表示編譯器不會檢查其內部狀態的執行緒安全。若此 mock 在多執行緒環境下被使用，可能導致資料競爭。建議確認其實際使用情境，若僅在測試中單執行緒使用，則可接受；否則應考慮改用 actor 或確保內部狀態的同步。

**判斷依據**：diff 中新增了 `@unchecked Sendable` 遵從。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 標註 @Sendable 可能造成不必要的限制</summary>

`getQueuedTabs` 的 completion handler 被加上 `@Sendable`，這要求閉包必須是 Sendable。若呼叫端傳入的閉包捕獲了非 Sendable 的狀態，可能會導致編譯錯誤。建議確認此變更是否必要，或考慮使用 `@MainActor` 隔離來替代。

**判斷依據**：diff 中將 `@escaping @MainActor` 改為 `@MainActor @Sendable @escaping`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8789 (cache hit 8704) ｜ completion tokens 1338 ｜ PR #6</sub>