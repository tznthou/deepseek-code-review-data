<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 相依套件版本（9.0.0-beta.25562.4 → 9.0.0-beta.25626.6），並包含多項建置基礎架構調整：將內部映像從 Mariner 2 改為 Azure Linux 3、source-index-stage1 條件改為僅限 main 分支、內部來源饋送 URL 變更、多處 PowerShell Invoke-WebRequest 加上 -UseBasicParsing、LocateVisualStudio 對缺少 vs 設定的防禦性處理，以及兩項測試相關變更（WebSocketCompressionTests 的 CSP 錯誤訊息正規化、RedisEndToEnd 測試隔離與 WebSocketWrapper 修正）。整體風險中等，主要疑慮在於 source-index-stage1 條件變更可能影響非 main 分支的來源索引行為，以及 WebSocketWrapper 的修改是否完整解決競態。建議確認這些變更的意圖與影響範圍。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/core-templates/job/source-index-stage1.yml:9` | source-index-stage1 條件改為僅限 main 分支可能導致其他分支無法進行來源索引 | 0.80 |
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408` | WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設位置變更可能引入競態 | 0.75 |
| 🔸 | Minor | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | CSP 錯誤訊息正規化使用兩個 Regex 可能過於嚴格 | 0.70 |
| 🔸 | Minor | `eng/common/tools.ps1:550` | LocateVisualStudio 中 $vsRequirements 可能為 $null 但後續未完全防護 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> source-index-stage1 條件改為僅限 main 分支可能導致其他分支無法進行來源索引</summary>

此變更將 `condition` 從空字串改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`，這會讓 source-index-stage1 作業只在 main 分支執行。若此作業原本用於所有分支的來源索引（例如用於符號伺服器或來源連結），則 release 分支或其他功能分支將不再產生索引，可能影響偵錯體驗或合規要求。請確認此變更的意圖，並考慮是否應改為排除 PR 分支或使用其他條件。

**判斷依據**：diff 中將原本的 `condition: ''` 改為 `condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')`，限制了作業的執行範圍。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408</code> WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設位置變更可能引入競態</summary>

原本在複製資料後才重設 `_receiveTcs`，現在改為在 await 之後立即重設。這可能導致在 `res.Item2.CopyTo(buffer)` 執行期間，另一個執行緒呼叫 `SetReceiveResult` 時會設定新的 `_receiveTcs`，但目前的 `ReceiveAsync` 仍在使用舊的 `res`，造成資料不一致或遺失。建議確認此變更是否為了解決特定問題，並考慮使用鎖定或更安全的同步機制。

**判斷依據**：diff 顯示 `_receiveTcs = new(...)` 從 `res.Item2.CopyTo(buffer)` 之後移到之前，改變了重設時機。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> CSP 錯誤訊息正規化使用兩個 Regex 可能過於嚴格</summary>

測試現在要求日誌訊息同時符合舊版與新版的正規表達式，但實際上瀏覽器可能只輸出一種格式。若兩種格式不會同時出現，此斷言將永遠失敗。建議確認實際日誌輸出，並改為使用 `Assert.Matches` 搭配單一正規表達式或使用 `Assert.True` 檢查任一符合。

**判斷依據**：diff 將原本的 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 改為同時檢查兩個 Regex 的 `Assert.True`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/tools.ps1:550</code> LocateVisualStudio 中 $vsRequirements 可能為 $null 但後續未完全防護</summary>

新增了當 `$GlobalJson.tools` 沒有 `vs` 屬性時將 `$vsRequirements` 設為 `$null` 的邏輯，但後續的 `if ($vsRequirements -and (Get-Member ...))` 已處理 null 情況。然而，若 `$vsRequirements` 為 null，`$args` 陣列仍會包含 `-requires Microsoft.Component.MSBuild` 等必要參數，這可能導致 vswhere 執行失敗。建議確認在沒有 vs 設定的情況下是否應跳過整個 Visual Studio 定位流程。

**判斷依據**：diff 新增了對 `$GlobalJson.tools` 缺少 `vs` 屬性的處理，但未改變後續使用 `$vsRequirements` 的邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8699 (cache hit 8576) ｜ completion tokens 1382 ｜ PR #2</sub>