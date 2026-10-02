<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量測試類別的 setUp/tearDown 改為 async 版本，並將 DependencyHelperMock.bootstrapDependencies() 標記為 @MainActor 且改為 async 呼叫。主要風險在於部分測試類別未正確處理 async 呼叫（例如 LaunchScreenViewModelTests 中未加 await），可能導致編譯錯誤或測試行為不一致。此外，刪除 TestSetup.swift 與移除 OnboardingMultipeChoiceButtonModel.swift 的專案引用，需確認無其他相依。整體改動方向合理，但需修正遺漏的 await 並確保所有呼叫點一致。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | bootstrapDependencies() 為 async 但呼叫處未加 await | 0.90 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28` | tearDown 中呼叫 reset() 未加 await | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11` | bootstrapDependencies 標記 @MainActor 但未標示為 async | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/TestSetup.swift:1` | 刪除 TestSetup.swift 可能影響其他測試 | 0.50 |
| 🔸 | Minor | `firefox-ios/Client.xcodeproj/project.pbxproj:14847` | 移除 OnboardingMultipeChoiceButtonModel.swift 引用 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> bootstrapDependencies() 為 async 但呼叫處未加 await</summary>

在 async setUp 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 時未加上 `await`，而該方法已改為 async（標記 @MainActor 且無同步版本）。這會導致編譯錯誤：`async call in a function that does not support concurrency`。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但呼叫 bootstrapDependencies 時未加 await，與其他檔案（如 FormAutofillHelperTests.swift）的修改不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28</code> tearDown 中呼叫 reset() 未加 await</summary>

`DependencyHelperMock().reset()` 可能也是 async 或需在主執行緒執行，但此處未加 await。若 reset 為同步方法則無問題，但需確認其簽名。

**判斷依據**：其他檔案如 LaunchTypeTests.swift 在 tearDown 中呼叫 reset 時未加 await，但此處 tearDown 已改為 async throws，若 reset 為 async 則需 await。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11</code> bootstrapDependencies 標記 @MainActor 但未標示為 async</summary>

方法標記為 @MainActor，但未明確標示為 async。在 Swift 中，@MainActor 方法若在非主執行緒呼叫，編譯器會要求 await。此處方法內有同步程式碼，但呼叫端需 await，因此方法應隱含 async。建議明確加上 `async` 關鍵字以提升可讀性。

**判斷依據**：diff 中方法宣告為 `@MainActor func bootstrapDependencies(...)`，但呼叫端均使用 `await`，表示方法為 async。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/TestSetup.swift:1</code> 刪除 TestSetup.swift 可能影響其他測試</summary>

TestSetup.swift 被刪除，且從專案檔中移除。需確認沒有其他測試類別依賴此類別進行初始化。若無相依則安全，但建議搜尋引用。

**判斷依據**：diff 顯示整個檔案被刪除，且專案檔中相關引用被移除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client.xcodeproj/project.pbxproj:14847</code> 移除 OnboardingMultipeChoiceButtonModel.swift 引用</summary>

從專案檔中移除了 `OnboardingMultipeChoiceButtonModel.swift` 的檔案引用，但未看到對應的檔案刪除。若檔案仍存在但未加入 target，可能導致編譯失敗或資源遺漏。需確認此檔案是否已不再使用。

**判斷依據**：diff 中刪除了該檔案的 PBXFileReference 和 PBXBuildFile 條目，但未見檔案刪除。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23648 (cache hit 23552) ｜ completion tokens 1224 ｜ PR #8</sub>