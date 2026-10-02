<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項基礎架構調整：將內部映像從 Mariner 2 升級至 Azure Linux 3、修正 source-index-stage1 的條件、更新內部 NuGet 來源 URL、在 PowerShell 的 Invoke-WebRequest 中加入 -UseBasicParsing、強化 LocateVisualStudio 對缺少 tools.vs 的處理、調整 WebSocket 壓縮測試的 CSP 錯誤訊息比對、隔離兩個不穩定的 Redis 測試，以及修正 WebSocketWrapper 的接收邏輯。整體風險中等，主要疑慮在於 Azure Linux 3 的相容性、條件變更可能影響來源索引產生，以及 WebSocketWrapper 的修改可能隱含競態條件。建議確認這些變更已在目標環境中驗證。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/core-templates/job/source-build.yml:68` | 內部來源建置映像從 Mariner 2 升級至 Azure Linux 3 可能導致相容性問題 | 0.70 |
| ⚠️ | Major | `eng/common/core-templates/job/source-index-stage1.yml:9` | source-index-stage1 條件變更可能影響來源索引產生 | 0.70 |
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409` | WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設位置可能導致競態條件 | 0.70 |
| 🔸 | Minor | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:103` | CSP 錯誤訊息比對使用兩個 Regex 可能過於嚴格 | 0.80 |
| 🔸 | Minor | `eng/common/tools.ps1:550` | LocateVisualStudio 對缺少 tools.vs 的處理可能改變行為 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-build.yml:68</code> 內部來源建置映像從 Mariner 2 升級至 Azure Linux 3 可能導致相容性問題</summary>

將內部來源建置的映像從 `1es-mariner-2` 改為 `1es-azurelinux-3`。Azure Linux 3 是較新的作業系統，可能包含不相容的套件或工具鏈變更，導致建置失敗或產出二進位檔的相容性問題。建議確認此變更已在內部管線中驗證，並檢查是否有相依於特定 OS 版本的工具或腳本。

**判斷依據**：diff 中將 `image: 1es-mariner-2` 改為 `image: 1es-azurelinux-3`

</details>

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> source-index-stage1 條件變更可能影響來源索引產生</summary>

將 `condition` 從空字串改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`。這會限制來源索引僅在主分支上執行。若某些發行分支也需要來源索引，此變更可能導致索引缺失。請確認此限制是否符合預期。

**判斷依據**：diff 中將 `condition: ''` 改為 `condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')`

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409</code> WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設位置可能導致競態條件</summary>

將 `_receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);` 移至 `await _receiveTcs.Task` 之後、零位元組讀取處理之前。這可能導致在零位元組讀取時，`_receiveTcs` 已被重設，但後續的 `SetReceiveResult` 可能設定到新的 TCS，而舊的 TCS 已完成，造成訊息遺失或錯誤。建議將重設邏輯放在處理完成後，或使用更安全的同步機制。

**判斷依據**：diff 中將 `_receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);` 從零位元組讀取處理之後移至之前

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:103</code> CSP 錯誤訊息比對使用兩個 Regex 可能過於嚴格</summary>

測試改為同時比對舊版和新版的 CSP 錯誤訊息。若瀏覽器更新後產生第三種格式，測試將失敗。建議使用單一 Regex 涵蓋所有可能格式，或使用更寬鬆的比對。

**判斷依據**：diff 中將 `Assert.Matches(ParseErrorMessage(), logs[0].Message);` 改為上述程式碼

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/tools.ps1:550</code> LocateVisualStudio 對缺少 tools.vs 的處理可能改變行為</summary>

當 `$GlobalJson.tools` 不存在 `vs` 屬性時，`$vsRequirements` 設為 `$null`，後續的 `Get-Member` 呼叫加上 `-ErrorAction SilentlyContinue` 以避免錯誤。這可能導致 `vswhere` 以不同參數執行，進而找到不符合需求的 Visual Studio 執行個體。建議確認此變更不會影響 VS 執行個體的選擇。

**判斷依據**：diff 中將原本的 `if (!$vsRequirements) { $vsRequirements = $GlobalJson.tools.vs }` 改為上述程式碼

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8518 (cache hit 1536) ｜ completion tokens 1459 ｜ PR #2</sub>