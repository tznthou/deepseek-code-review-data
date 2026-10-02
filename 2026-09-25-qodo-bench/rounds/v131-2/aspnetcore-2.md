<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項建置與測試基礎架構的調整。整體風險偏低，但需注意 `source-index-stage1.yml` 中 condition 的變更可能影響非 main 分支的索引行為，以及 `tools.ps1` 中對 `$vsRequirements` 的處理可能改變 Visual Studio 偵測邏輯。建議確認這些變更符合預期。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/core-templates/job/source-index-stage1.yml:9` | condition 變更可能導致非 main 分支無法執行 source index | 0.70 |
| 🔸 | Minor | `eng/common/tools.ps1:550` | Visual Studio 需求處理邏輯變更可能影響建置 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> condition 變更可能導致非 main 分支無法執行 source index</summary>

原本 condition 為空字串（代表永遠執行），現在改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`，這會讓 source index 只在 main 分支執行。如果其他分支（例如 release 分支）也需要 source index，此變更會造成功能遺失。請確認此限制是否為預期行為。

**判斷依據**：diff 中將 condition 從空字串改為特定分支條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/tools.ps1:550</code> Visual Studio 需求處理邏輯變更可能影響建置</summary>

原本直接指派 `$vsRequirements = $GlobalJson.tools.vs`，現在改為先檢查 `vs` 屬性是否存在，若不存在則設為 `$null`。後續使用 `$vsRequirements` 時也增加了 null 檢查。這項變更可能影響 Visual Studio 的偵測與參數傳遞，請確認在沒有 `vs` 設定的情況下行為仍符合預期。

**判斷依據**：diff 中新增了條件判斷與 null 指派。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6488 (cache hit 6400) ｜ completion tokens 580 ｜ PR #2</sub>