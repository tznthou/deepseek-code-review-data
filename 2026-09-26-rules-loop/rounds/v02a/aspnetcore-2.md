<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項建置腳本與測試的調整。整體風險中等，需特別注意 `eng/common/tools.ps1` 中 `LocateVisualStudio` 函式的變更：當 `$GlobalJson.tools` 不存在 `vs` 屬性時，`$vsRequirements` 會被設為 `$null`，後續的 `Get-Member` 呼叫可能因 `$null` 輸入而拋出錯誤，導致建置失敗。此外，`WebSocketCompressionTests.cs` 的測試邏輯改為同時匹配新舊兩種錯誤訊息，但若瀏覽器產生其他格式的錯誤訊息，測試將失敗。建議優先修正 `LocateVisualStudio` 的 null 處理，並確認測試變更的相容性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/tools.ps1:564` | LocateVisualStudio 中 $vsRequirements 可能為 $null 導致後續 Get-Member 失敗 | 0.80 |
| 🔸 | Minor | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 測試同時匹配新舊錯誤訊息可能過於嚴格 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/tools.ps1:564</code> LocateVisualStudio 中 $vsRequirements 可能為 $null 導致後續 Get-Member 失敗</summary>

在 `LocateVisualStudio` 函式中，當 `$GlobalJson.tools` 沒有 `vs` 屬性時，`$vsRequirements` 被設為 `$null`。後續的 `if ($vsRequirements -and (Get-Member -InputObject $vsRequirements -Name 'version' -ErrorAction SilentlyContinue))` 雖然有 `$vsRequirements -and` 的條件，但 PowerShell 的 `-and` 運算子會先評估左側，若為 `$false` 則不會評估右側，因此不會呼叫 `Get-Member`。然而，若 `$vsRequirements` 是空陣列或空字串，`-and` 的結果可能為 `$false`，但 `Get-Member` 仍可能被呼叫（取決於 PowerShell 版本和型別）。更安全的做法是明確檢查 `$null -ne $vsRequirements`。建議改為：
```powershell
if ($null -ne $vsRequirements -and (Get-Member -InputObject $vsRequirements -Name 'version' -ErrorAction SilentlyContinue)) {
```
以避免潛在的 null 參考錯誤。

**判斷依據**：diff 中新增了 `$vsRequirements = $null` 的賦值，且後續的條件判斷使用 `$vsRequirements -and ...`，可能因 PowerShell 的 truthiness 判斷而導致非預期行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 測試同時匹配新舊錯誤訊息可能過於嚴格</summary>

測試改為同時匹配 `ParseErrorMessageRegexOld` 和 `ParseErrorMessageRegexNew`，但實際的錯誤訊息可能因瀏覽器版本或環境而異，導致測試不穩定。建議考慮使用單一正則表達式涵蓋兩種格式，或使用 `Assert.Matches` 逐一檢查。

**判斷依據**：diff 中將原本的 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 改為同時檢查兩個正則表達式，可能導致測試在部分環境下失敗。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8709 (cache hit 1536) ｜ completion tokens 912 ｜ PR #2</sub>