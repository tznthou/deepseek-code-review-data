<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async 版本，並為部分 UI 相關測試類別加上 @MainActor，同時調整了幾個 mock 類別以符合 Swift 6 的 Sendable 要求。整體變更方向正確，有助於消除 Swift 6 遷移中的警告。但需注意：NotificationManagerTests 中將 XCTAssert 改為 assert 可能導致測試失效；部分測試類別未加上 @MainActor 可能仍有併發警告；MockProfile 中的 getQueuedTabs 補上 @Sendable 是正確的，但需確認所有實作都同步更新。建議優先修正 assert 的使用，並全面檢查測試類別的 actor isolation。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssert 可能導致測試失效 | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 而非 XCTAssert 違反測試慣例 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14` | 測試類別未加上 @MainActor 可能仍有併發警告 | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | getQueuedTabs 的 completion 加上 @Sendable 可能影響呼叫端 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssert 可能導致測試失效</summary>

在測試方法中，將原本的 `XCTAssertTrue` 改為 Swift 標準庫的 `assert`。`assert` 在 Release 建置中會被編譯器移除，且 XCTest 不會將其視為測試斷言，因此即使條件為 false，測試仍會通過。這會讓測試失去驗證功能。

建議改回使用 `XCTAssertTrue`，或若因 actor isolation 無法直接使用，可考慮將斷言移到 MainActor 隔離的區塊中，或使用 `XCTAssert` 的 async 版本。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，且 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 而非 XCTAssert 違反測試慣例</summary>

XCTest 測試應使用 XCTest 框架的斷言（如 XCTAssertTrue）以正確回報失敗。使用標準庫的 `assert` 會讓測試在 Debug 模式下可能 crash，在 Release 模式下完全失效，且 XCTest 無法記錄失敗。建議改回 `XCTAssertTrue`。

**判斷依據**：diff 中將 `XCTAssertTrue` 改為 `assert`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14</code> 測試類別未加上 @MainActor 可能仍有併發警告</summary>

此測試類別操作 UI 相關物件（FxAWebViewModel），但未加上 `@MainActor`。在 Swift 6 嚴格併發檢查下，若這些物件或方法要求 MainActor 隔離，測試方法可能會產生編譯警告或錯誤。建議確認此類別是否需要加上 `@MainActor`，或將相關屬性標記為 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他 UI 相關測試類別（如 StoriesFeedDiffableDataSourceTests）已加上。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> getQueuedTabs 的 completion 加上 @Sendable 可能影響呼叫端</summary>

將 completion 閉包標記為 `@Sendable` 是為了符合 Swift 6 的併發安全要求，但這可能要求所有傳入的閉包也必須是 `@Sendable`。若呼叫端傳入的閉包捕獲了非 Sendable 的狀態，可能會產生編譯錯誤。建議確認所有呼叫端都能滿足此要求，或考慮使用 `@preconcurrency` 標記以漸進式遷移。

**判斷依據**：diff 中將 `completion: @escaping @MainActor ([ShareItem]) -> Void` 改為 `completion: @MainActor @Sendable @escaping ([ShareItem]) -> Void`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9991 (cache hit 9984) ｜ completion tokens 1222 ｜ PR #6</sub>