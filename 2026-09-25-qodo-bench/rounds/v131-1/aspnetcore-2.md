<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項建置基礎架構調整，例如將內部容器映像從 Mariner 2 升級至 Azure Linux 3、更新內部 NuGet 來源 URL、在 PowerShell 的 Invoke-WebRequest 加上 -UseBasicParsing 參數，以及調整 source-index-stage1 的執行條件。此外，也包含測試相關變更：放寬 WebSocket 壓縮測試的錯誤訊息比對、將兩個 Redis 測試標記為隔離（Quarantined），並修正 WebSocketWrapper 的競態條件。整體風險中等，主要疑慮在於建置基礎架構變更可能影響 CI/CD 穩定性，以及測試隔離可能掩蓋真實問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/core-templates/job/source-build.yml:68` | 內部容器映像從 Mariner 2 升級至 Azure Linux 3 可能導致建置失敗 | 0.80 |
| ⚠️ | Major | `eng/common/core-templates/steps/source-build.yml:44` | 內部 NuGet 來源 URL 變更可能導致下載失敗 | 0.80 |
| ⚠️ | Major | `eng/common/core-templates/job/source-index-stage1.yml:9` | source-index-stage1 條件變更可能導致索引作業未執行 | 0.70 |
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92` | 將測試標記為隔離可能掩蓋真實問題 | 0.70 |
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188` | 將測試標記為隔離可能掩蓋真實問題 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409` | WebSocketWrapper 的競態條件修正可能不完整 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-build.yml:68</code> 內部容器映像從 Mariner 2 升級至 Azure Linux 3 可能導致建置失敗</summary>

將 `image` 從 `1es-mariner-2` 改為 `1es-azurelinux-3` 可能導致相依性不相容或建置腳本在舊版映像上才能正常運作。若 Azure Linux 3 缺少某些必要套件或工具，內部建置管線可能中斷。建議確認此映像已通過完整驗證，或先在測試管線中試行。

**判斷依據**：diff 中 `eng/common/core-templates/job/source-build.yml` 第 68 行將 `image: 1es-mariner-2` 改為 `image: 1es-azurelinux-3`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/steps/source-build.yml:44</code> 內部 NuGet 來源 URL 變更可能導致下載失敗</summary>

將 `DotNetRuntimeSourceFeed` 從 `https://dotnetbuilds.blob.core.windows.net/internal` 改為 `https://ci.dot.net/internal` 可能導致驗證或網路設定問題。若新 URL 未正確設定權限或 DNS，內部建置將無法下載執行階段。建議確認新 URL 可從建置代理程式存取，且權杖仍有效。

**判斷依據**：diff 中 `eng/common/core-templates/steps/source-build.yml` 第 44 行將 URL 從 `https://dotnetbuilds.blob.core.windows.net/internal` 改為 `https://ci.dot.net/internal`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> source-index-stage1 條件變更可能導致索引作業未執行</summary>

將 `condition` 從空字串改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')` 會限制索引僅在主分支執行。若某些發行分支也需要索引，此變更可能導致索引缺失。建議確認此條件符合預期，或改用更彈性的條件。

**判斷依據**：diff 中 `eng/common/core-templates/job/source-index-stage1.yml` 第 9 行將 `condition: ''` 改為 `condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92</code> 將測試標記為隔離可能掩蓋真實問題</summary>

新增 `[QuarantinedTest]` 屬性會使測試在 CI 中暫時停用，可能導致相關錯誤被忽略。若問題未在隔離期間修復，可能累積技術債。建議確認隔離原因並追蹤修復進度。

**判斷依據**：diff 中 `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs` 第 92 行新增 `[QuarantinedTest]` 屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188</code> 將測試標記為隔離可能掩蓋真實問題</summary>

新增 `[QuarantinedTest]` 屬性會使測試在 CI 中暫時停用，可能導致相關錯誤被忽略。若問題未在隔離期間修復，可能累積技術債。建議確認隔離原因並追蹤修復進度。

**判斷依據**：diff 中 `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs` 第 188 行新增 `[QuarantinedTest]` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409</code> WebSocketWrapper 的競態條件修正可能不完整</summary>

將 `_receiveTcs` 的重設移至 `ReceiveAsync` 開頭，可避免在零位元組讀取時未重設的問題。但若 `ReceiveAsync` 在等待 `_receiveTcs.Task` 時被取消，可能導致 `_receiveTcs` 未重設，影響後續呼叫。建議考慮在 `finally` 區塊中重設，或使用更安全的同步機制。

**判斷依據**：diff 中 `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs` 第 409 行將 `_receiveTcs` 的重設移至 `ReceiveAsync` 開頭。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6488 (cache hit 1408) ｜ completion tokens 1672 ｜ PR #2</sub>