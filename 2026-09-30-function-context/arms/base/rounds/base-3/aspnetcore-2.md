<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本（9.0.0-beta.25562.4 → 9.0.0-beta.25626.6），並包含多項建置與測試基礎架構的調整。主要風險在於 `source-index-stage1.yml` 中 condition 的變更可能導致非 main 分支的 source index 工作被略過，以及 `WebSocketCompressionTests.cs` 中測試斷言邏輯的變更可能使測試無法正確捕捉錯誤。整體變更看似合理，但建議確認 condition 變更的意圖與測試斷言的覆蓋範圍。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/core-templates/job/source-index-stage1.yml:9` | source-index-stage1 的 condition 變更可能導致非 main 分支的 source index 工作被略過 | 0.75 |
| ⚠️ | Major | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 測試斷言邏輯變更可能導致測試無法正確捕捉錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> source-index-stage1 的 condition 變更可能導致非 main 分支的 source index 工作被略過</summary>

原本 condition 為空字串（表示永遠執行），現在改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`。這會使得在非 main 分支（例如 release 分支或 PR 分支）上，此工作不會執行。若 source index 是必要的建置步驟，這可能導致非 main 分支的建置缺少 source index 資料，影響後續的符號或來源對應。請確認此變更是否為預期行為，並考慮是否應使用更寬鬆的條件（例如排除 PR 分支但包含 release 分支）。

**判斷依據**：diff 中 condition 從空字串改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`，這會限制此工作只在 main 分支執行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 測試斷言邏輯變更可能導致測試無法正確捕捉錯誤</summary>

原本使用 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 檢查單一正則表達式，現在改為同時檢查兩個正則表達式（`ParseErrorMessageRegexOld` 和 `ParseErrorMessageRegexNew`）都必須匹配。這可能過於嚴格：如果實際錯誤訊息只符合其中一種模式，測試就會失敗。請確認是否應使用 `||` 而非 `&&`，或者是否預期錯誤訊息同時包含兩種模式。

**判斷依據**：diff 中將原本的 `Assert.Matches` 改為 `Assert.True` 並使用 `&&` 結合兩個正則表達式，但錯誤訊息通常只會符合其中一種模式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6524 (cache hit 6400) ｜ completion tokens 771 ｜ PR #2</sub>