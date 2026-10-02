<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將大量測試類別的 setUp/tearDown 改為 async 版本，並將 DependencyHelperMock.bootstrapDependencies() 標記為 @MainActor 且改為 async 呼叫。主要風險在於部分測試類別未正確處理 async 呼叫（例如 LaunchScreenViewModelTests 中未加 await），可能導致編譯錯誤或測試行為不一致。另外，刪除 TestSetup.swift 與移除部分檔案引用可能影響測試建置。整體方向正確，但需修正遺漏的 await 與確認刪除檔案無其他依賴。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | async setUp 中呼叫 @MainActor async 方法缺少 await | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | setUp 中呼叫 @MainActor 方法可能造成執行緒問題 | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11` | bootstrapDependencies 標記 @MainActor 但未處理非 MainActor 呼叫 | 0.85 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/TestSetup.swift:1` | 刪除 TestSetup.swift 可能影響其他測試 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client.xcodeproj/project.pbxproj:13745` | 移除 TestSetup.swift 的檔案引用 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client.xcodeproj/project.pbxproj:14844` | 移除 OnboardingMultipeChoiceButtonModel.swift 引用 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client.xcodeproj/project.pbxproj:18982` | 移除 Locale+possibilitiesForLanguageIdentifier.swift 引用 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> async setUp 中呼叫 @MainActor async 方法缺少 await</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()`，但該方法已標記為 `@MainActor` 且為 async，此處未加 `await`，將導致編譯錯誤。

建議改為：
```swift
await DependencyHelperMock().bootstrapDependencies()
```

**判斷依據**：diff 中該行未加 await，而其他檔案（如 FormAutofillHelperTests.swift）已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> setUp 中呼叫 @MainActor 方法可能造成執行緒問題</summary>

`bootstrapDependencies` 現在是 `@MainActor`，但此測試類別未標記為 `@MainActor`，且 `setUp` 為 async，呼叫時若未在 MainActor 上執行，可能導致 runtime crash 或資料競爭。建議將測試類別標記為 `@MainActor` 或確保在 MainActor 上呼叫。

**判斷依據**：其他測試類別如 `DownloadProgressManagerTests` 有標記 `@MainActor`，此處未標記。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11</code> bootstrapDependencies 標記 @MainActor 但未處理非 MainActor 呼叫</summary>

將 `bootstrapDependencies` 標記為 `@MainActor` 後，所有呼叫端都必須在 MainActor 上執行。但仍有部分測試類別（如 `LaunchScreenViewModelTests`）未標記 `@MainActor`，且呼叫時未使用 `await`，可能導致編譯錯誤或 runtime 問題。建議全面檢查所有呼叫端，確保在 MainActor 上呼叫或使用 `await MainActor.run`。

**判斷依據**：diff 中新增 `@MainActor` 屬性，但未修改所有呼叫端。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/TestSetup.swift:1</code> 刪除 TestSetup.swift 可能影響其他測試</summary>

刪除 `TestSetup.swift` 檔案，但該檔案可能被其他測試或程式碼引用。若仍有引用，將導致編譯失敗。建議確認所有引用已移除。

**判斷依據**：diff 顯示整個檔案被刪除，但未確認其他檔案是否引用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client.xcodeproj/project.pbxproj:13745</code> 移除 TestSetup.swift 的檔案引用</summary>

從專案檔中移除 `TestSetup.swift` 的引用，但若該檔案仍存在於檔案系統中，可能造成專案不一致。建議確認檔案已刪除。

**判斷依據**：diff 中移除該行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client.xcodeproj/project.pbxproj:14844</code> 移除 OnboardingMultipeChoiceButtonModel.swift 引用</summary>

從專案檔中移除 `OnboardingMultipeChoiceButtonModel.swift` 的引用，但未看到對應的檔案刪除。若檔案仍存在，可能造成專案不一致。

**判斷依據**：diff 中移除該行，但未見檔案刪除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client.xcodeproj/project.pbxproj:18982</code> 移除 Locale+possibilitiesForLanguageIdentifier.swift 引用</summary>

從專案檔中移除 `Locale+possibilitiesForLanguageIdentifier.swift` 的引用，但未看到對應的檔案刪除。若檔案仍存在，可能造成專案不一致。

**判斷依據**：diff 中移除該行，但未見檔案刪除。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 21553 (cache hit 1408) ｜ completion tokens 1536 ｜ PR #8</sub>