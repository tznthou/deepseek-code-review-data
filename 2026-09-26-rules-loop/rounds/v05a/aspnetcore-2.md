<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本（9.0.0-beta.25562.4 → 9.0.0-beta.25626.6），並包含多項建置基礎架構調整：將內部映像從 Mariner 2 升級至 Azure Linux 3、修改 source-index-stage1 的執行條件、更新內部套件來源 URL、在 PowerShell 的 Invoke-WebRequest 加上 -UseBasicParsing、強化 LocateVisualStudio 對缺少 vs 設定的處理，以及修正 WebSocketCompressionTests 的斷言與 RedisEndToEnd 測試的隔離與資源釋放順序。整體風險中等，主要疑慮在於測試斷言邏輯的變更可能掩蓋真實錯誤，以及 WebSocketWrapper 的 ReceiveAsync 修改可能引入競態。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 測試斷言改為同時符合新舊 Regex 可能導致測試永遠失敗或失去驗證意義 | 0.80 |
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408` | WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重置時機可能導致競態或遺失資料 | 0.75 |
| 🔸 | Minor | `eng/common/core-templates/job/source-index-stage1.yml:9` | source-index-stage1 條件變更可能影響非 main 分支的索引行為 | 0.70 |
| 🔸 | Minor | `eng/common/tools.ps1:550` | LocateVisualStudio 中 $vsRequirements 可能為 $null 但後續未完全防護 | 0.65 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213` | DisposeAsync 順序調整可能影響測試穩定性 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 測試斷言改為同時符合新舊 Regex 可能導致測試永遠失敗或失去驗證意義</summary>

原本斷言 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 只驗證單一錯誤訊息格式。修改後改為 `Assert.True(ParseErrorMessageRegexOld.IsMatch(...) && ParseErrorMessageRegexNew.IsMatch(...))`，要求同一則日誌同時符合兩個不同的 Regex。這兩個 Regex 分別對應不同的錯誤訊息格式（'Refused to frame' 與 'Framing ... violates'），同一則日誌不可能同時符合兩者，因此此斷言將永遠失敗，或若日誌內容恰好包含兩種模式則可能誤判。建議改為 `Assert.True(ParseErrorMessageRegexOld.IsMatch(...) || ParseErrorMessageRegexNew.IsMatch(...))`，或分別驗證不同日誌。

**判斷依據**：diff 中新增的 `Assert.True` 使用 `&&` 運算子，但兩個 Regex 模式互斥，不可能同時匹配同一字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408</code> WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重置時機可能導致競態或遺失資料</summary>

原本在複製資料後才重置 `_receiveTcs`，現在改為在 await 之後立即重置。若 `buffer.Count == 0` 的分支直接返回，則 `_receiveTcs` 已被重置，但呼叫端可能預期後續呼叫能取得相同結果。此外，若 `res.Item2.CopyTo(buffer)` 拋出例外，`_receiveTcs` 已重置，但資料未完整複製，可能導致狀態不一致。建議將重置邏輯移至 finally 區塊或確保在所有路徑中正確處理。

**判斷依據**：diff 顯示 `_receiveTcs = new(...)` 被移至 `if (buffer.Count == 0)` 之前，且未在例外路徑中恢復。

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> source-index-stage1 條件變更可能影響非 main 分支的索引行為</summary>

原本 `condition: ''` 表示無條件執行，現在改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`，僅在 main 分支執行。若其他分支（如 release 分支）也需要 source indexing，此變更將導致功能遺失。請確認此限制是否符合預期。

**判斷依據**：diff 顯示 condition 從空字串改為特定分支條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/tools.ps1:550</code> LocateVisualStudio 中 $vsRequirements 可能為 $null 但後續未完全防護</summary>

新增了當 `$GlobalJson.tools` 缺少 `vs` 屬性時將 `$vsRequirements` 設為 `$null` 的邏輯，並在後續 `Get-Member` 檢查中加入 `$vsRequirements -and` 條件。但若 `$vsRequirements` 為 `$null`，`$args` 陣列仍會包含 `-requires Microsoft.Component.MSBuild` 等參數，可能導致 vswhere 執行失敗。建議在 `$vsRequirements` 為 `$null` 時提前返回或調整參數。

**判斷依據**：diff 顯示新增的 null 處理，但後續 `$args` 建構未考慮 null 情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213</code> DisposeAsync 順序調整可能影響測試穩定性</summary>

原本先釋放 `connection` 再釋放 `secondConnection`，現在順序相反。若兩個連線之間存在相依性（例如共用資源），此變更可能導致測試行為改變。建議確認此調整是否為解決特定問題所需，並確保不會引入新的不穩定因素。

**判斷依據**：diff 顯示兩行順序對調。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8643 (cache hit 6528) ｜ completion tokens 1625 ｜ PR #2</sub>