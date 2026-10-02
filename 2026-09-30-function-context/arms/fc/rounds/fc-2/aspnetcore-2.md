<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 相依性版本，並包含數個基礎架構與測試的修正。主要風險在於 `LocateVisualStudio` 函式對 `$vsRequirements` 的處理，當 `$GlobalJson.tools` 不存在 `vs` 屬性時，後續的 `Get-Member` 呼叫可能因 `$null` 而拋出錯誤。此外，`source-index-stage1.yml` 的 condition 變更可能影響非 main 分支的索引行為。整體而言，變更範圍明確，但建議修正上述問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/tools.ps1:550` | LocateVisualStudio 中 $vsRequirements 可能為 $null 導致後續 Get-Member 失敗 | 0.80 |
| 🔸 | Minor | `eng/common/core-templates/job/source-index-stage1.yml:9` | source-index-stage1 的 condition 變更可能影響非 main 分支的索引 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/tools.ps1:550</code> LocateVisualStudio 中 $vsRequirements 可能為 $null 導致後續 Get-Member 失敗</summary>

在 `LocateVisualStudio` 函式中，當 `$GlobalJson.tools` 不存在 `vs` 屬性時，`$vsRequirements` 會被設為 `$null`。然而，後續的 `if ($vsRequirements -and (Get-Member -InputObject $vsRequirements -Name 'version' -ErrorAction SilentlyContinue))` 雖然有 `$vsRequirements -and` 的短路保護，但 `Get-Member` 的 `-InputObject` 參數若為 `$null`，在某些 PowerShell 版本中仍可能拋出錯誤（例如「Cannot bind argument to parameter 'InputObject' because it is null」）。建議先檢查 `$vsRequirements` 是否為 `$null`，或改用 `if ($null -ne $vsRequirements -and (Get-Member ...))` 的方式。

**判斷依據**：diff 中新增了 `$vsRequirements = $null` 的分支，且後續的 `Get-Member` 呼叫使用了 `$vsRequirements` 作為 `-InputObject`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> source-index-stage1 的 condition 變更可能影響非 main 分支的索引</summary>

原本 `condition` 為空字串，代表所有分支都會執行 source-index-stage1。現在改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`，這會讓非 main 分支（例如 release 分支或 PR 分支）不再執行此階段。如果這是預期的行為（例如只在 main 分支產生索引），則沒有問題；但若其他分支也需要索引，則可能造成遺漏。建議確認此變更的意圖。

**判斷依據**：diff 中將 `condition: ''` 改為 `condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8518 (cache hit 8448) ｜ completion tokens 885 ｜ PR #2</sub>