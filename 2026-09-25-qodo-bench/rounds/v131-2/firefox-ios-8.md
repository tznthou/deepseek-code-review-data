<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將大量測試類別的 setUp/tearDown 改為 async 版本，並將 DependencyHelperMock.bootstrapDependencies() 標記為 @MainActor 且改為 async 呼叫。主要風險在於部分測試類別未正確處理 async 呼叫（例如 LaunchScreenViewModelTests 中未加 await），可能導致編譯錯誤或測試行為不一致。另外，刪除 TestSetup.swift 與移除 OnboardingMultipeChoiceButtonModel.swift 的引用需確認無其他相依。整體改動方向合理，但需修正遺漏的 await 並確保所有呼叫點一致。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | async setUp 中呼叫 bootstrapDependencies 缺少 await | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28` | tearDown 中呼叫 reset 未處理 async 或順序 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11` | bootstrapDependencies 標記 @MainActor 但未處理非主執行緒呼叫 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/TestSetup.swift:1` | 刪除 TestSetup.swift 可能影響其他測試 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client.xcodeproj/project.pbxproj:14847` | 移除 OnboardingMultipeChoiceButtonModel.swift 引用 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> async setUp 中呼叫 bootstrapDependencies 缺少 await</summary>

在 async setUp 方法中，`DependencyHelperMock().bootstrapDependencies()` 現在是 async 方法，但此處未加上 `await`，會導致編譯錯誤。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中該行未加上 await，而其他檔案均已加上 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28</code> tearDown 中呼叫 reset 未處理 async 或順序</summary>

tearDown 改為 async throws 後，`DependencyHelperMock().reset()` 仍為同步呼叫，但若 reset 未來改為 async 可能遺漏。目前 reset 為同步，但建議確認 reset 是否也需 await。

**判斷依據**：diff 中 tearDown 改為 async throws，但 reset 未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11</code> bootstrapDependencies 標記 @MainActor 但未處理非主執行緒呼叫</summary>

方法標記 @MainActor 後，所有呼叫者必須在主執行緒或使用 await。但部分測試類別可能未在主執行緒呼叫（例如非 @MainActor 的 setUp），若未加 await 會導致編譯錯誤或 runtime crash。請確認所有呼叫點均已正確處理。

**判斷依據**：diff 中新增 @MainActor，但部分呼叫點未加 await（如 LaunchScreenViewModelTests）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/TestSetup.swift:1</code> 刪除 TestSetup.swift 可能影響其他測試</summary>

TestSetup.swift 被刪除，且從 project.pbxproj 移除。需確認沒有其他測試檔案依賴此類別。

**判斷依據**：diff 顯示檔案被刪除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client.xcodeproj/project.pbxproj:14847</code> 移除 OnboardingMultipeChoiceButtonModel.swift 引用</summary>

從 project.pbxproj 移除 OnboardingMultipeChoiceButtonModel.swift 的引用，但未看到檔案刪除。若檔案仍存在，可能導致專案不一致。

**判斷依據**：diff 中移除了該行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 21553 (cache hit 21504) ｜ completion tokens 1043 ｜ PR #8</sub>