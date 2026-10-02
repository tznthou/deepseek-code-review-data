<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項建置與測試基礎架構的調整。主要風險在於 `WebSocketCompressionTests.cs` 中測試斷言邏輯的變更：原本應匹配單一錯誤訊息格式，現在改為同時要求匹配新舊兩種正則表達式，這可能導致測試永遠失敗或無法正確驗證。此外，`source-index-stage1.yml` 的 condition 變更可能影響來源索引建置的觸發範圍。整體而言，變更集中且多數為例行性更新，但測試邏輯的變更需要進一步確認。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 測試斷言同時要求新舊正則表達式匹配，可能導致測試永遠失敗 | 0.90 |
| 🔸 | Minor | `eng/common/core-templates/job/source-index-stage1.yml:9` | condition 變更可能限制來源索引建置的觸發範圍 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 測試斷言同時要求新舊正則表達式匹配，可能導致測試永遠失敗</summary>

原本的 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 只要求匹配單一正則表達式。修改後改為 `Assert.True(ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ...)`，這要求同一條日誌訊息同時匹配兩個不同的正則表達式。這兩個正則表達式分別對應不同的錯誤訊息格式（'Refused to frame' 與 'Framing ... violates'），同一條日誌不可能同時符合兩者，因此此斷言將永遠失敗。建議改為使用 `Assert.Matches` 搭配單一正則表達式，或使用 `Assert.True` 檢查是否匹配其中一個（使用 `||` 運算子）。

**判斷依據**：diff 中新增的 `Assert.True` 使用 `&&` 運算子結合兩個 `IsMatch` 呼叫，而兩個正則表達式分別對應不同的錯誤訊息格式，不可能同時匹配。

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> condition 變更可能限制來源索引建置的觸發範圍</summary>

原本 `condition: ''` 表示無條件執行，現在改為 `condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')`，這將使來源索引建置僅在 main 分支上執行。如果這是預期的行為（例如避免在 PR 或 release 分支上執行），則沒有問題；但若來源索引建置原本需要在其他分支上執行，此變更可能導致建置流程中斷。建議確認此變更的意圖，並確保其他分支的建置不會因此缺少來源索引。

**判斷依據**：diff 中將原本的 `condition: ''` 改為 `condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')`，限制了執行條件。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8719 (cache hit 6400) ｜ completion tokens 823 ｜ PR #2</sub>