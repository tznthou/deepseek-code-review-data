<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試類別遷移至 Swift 6 的 async setUp/tearDown 模式，並加入 @MainActor 標註與 Sendable 一致性調整。整體變更符合 Swift 6 遷移方向，但部分測試類別未加上 @MainActor 標註，可能導致 UI 相關程式碼在背景執行緒執行而產生問題。此外，NotificationManagerTests 中將 XCTAssertTrue 改為 assert 可能導致測試在 release 建置中失效。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:15` | 缺少 @MainActor 標註可能導致 UI 操作在背景執行緒執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14` | 缺少 @MainActor 標註可能導致 UI 操作在背景執行緒執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11` | 移除 @MainActor 標註可能導致 UI 操作在背景執行緒執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93` | completion handler 的 @Sendable 標註可能導致不必要的限制 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:15</code> 缺少 @MainActor 標註可能導致 UI 操作在背景執行緒執行</summary>

此測試類別操作 UI 元件（SyncContentSettingsViewController），但未加上 @MainActor 標註。在 Swift 6 中，若測試方法未標註 @MainActor，則 setUp/tearDown 可能不在主執行緒執行，導致 UI 相關操作失敗或產生不可預期的行為。建議在類別宣告前加上 @MainActor。

**判斷依據**：diff 中此類別未新增 @MainActor，但其他 UI 測試類別（如 StoriesFeedDiffableDataSourceTests）已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14</code> 缺少 @MainActor 標註可能導致 UI 操作在背景執行緒執行</summary>

此測試類別操作 UI 相關元件（FxAWebViewModel），但未加上 @MainActor 標註。在 Swift 6 中，若測試方法未標註 @MainActor，則 setUp/tearDown 可能不在主執行緒執行，導致 UI 相關操作失敗或產生不可預期的行為。建議在類別宣告前加上 @MainActor。

**判斷依據**：diff 中此類別未新增 @MainActor，但其他 UI 測試類別（如 StoriesFeedDiffableDataSourceTests）已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11</code> 移除 @MainActor 標註可能導致 UI 操作在背景執行緒執行</summary>

此測試類別原本有 @MainActor 標註，但在此 PR 中被移除。若測試方法涉及 UI 操作，移除 @MainActor 可能導致測試在背景執行緒執行，造成不可預期的行為。建議確認此類別是否真的不需要 @MainActor，若需要則應保留。

**判斷依據**：diff 中移除了 @MainActor 標註。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效</summary>

將 XCTAssertTrue 改為 assert 可能導致測試在 release 建置中失效，因為 assert 在最佳化編譯時可能被移除。建議使用 XCTest 的斷言方法（如 XCTAssertTrue）以確保測試在各種建置中都能正常執行。

**判斷依據**：diff 中將原本的 XCTAssertTrue 改為 assert。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Mocks/MockProfile.swift:93</code> completion handler 的 @Sendable 標註可能導致不必要的限制</summary>

在 getQueuedTabs 的 completion handler 中加入 @Sendable 標註，可能導致呼叫端必須使用 @Sendable closure，增加不必要的限制。若無跨執行緒傳遞的需求，建議移除 @Sendable。

**判斷依據**：diff 中新增了 @Sendable 標註。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7906 (cache hit 1408) ｜ completion tokens 1189 ｜ PR #6</sub>