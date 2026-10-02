<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項建置管線與測試的調整。整體風險中等，需注意來源索引條件變更可能影響非 main 分支的索引行為，以及 WebSocket 測試中接收結果重設時機的變更可能引入競態。建議合併前確認這些變更的影響。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/core-templates/job/source-index-stage1.yml:9` | 來源索引條件變更可能導致非 main 分支無法索引 | 0.80 |
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408` | WebSocketWrapper 中 _receiveTcs 重設時機可能導致競態 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362` | [R14] 內部類別 WebSocketWrapper 未標記 sealed | 0.90 |
| 🔸 | Minor | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 測試斷言使用兩個 Regex 同時匹配可能過於嚴格 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> 來源索引條件變更可能導致非 main 分支無法索引</summary>

將 `condition` 從空字串改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`，這會使來源索引僅在 main 分支執行。若其他分支（如 release 分支）也需要來源索引，此變更將導致索引遺漏，影響符號伺服器與偵錯體驗。建議確認此限制是否為預期行為，或改用更寬鬆的條件（例如排除 PR 分支）。

**判斷依據**：diff 中將原本的 `condition: ''` 改為 `condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')`，限制了執行分支。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408</code> WebSocketWrapper 中 _receiveTcs 重設時機可能導致競態</summary>

在 `ReceiveAsync` 中，原本在處理零位元組讀取後才重設 `_receiveTcs`，現在改為在取得結果後立即重設。若 `buffer.Count == 0` 時直接回傳，新的 `_receiveTcs` 已建立，但呼叫端可能預期後續讀取會等待新的結果。此變更可能影響測試的同步邏輯，建議確認是否為修正特定問題所需，並評估對其他測試的影響。

**判斷依據**：diff 顯示 `_receiveTcs = new(...)` 被移至 `if (buffer.Count == 0)` 之前，改變了重設時機。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362</code> [R14] 內部類別 WebSocketWrapper 未標記 sealed</summary>

根據規範 R14，內部實作類別若未預期被繼承應標記為 `sealed`。此變更移除了 `sealed` 修飾詞，可能違反效能與設計意圖。若無繼承需求，建議保留 `sealed`。

**判斷依據**：diff 中 `internal sealed class WebSocketWrapper` 改為 `internal class WebSocketWrapper`，移除了 `sealed`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 測試斷言使用兩個 Regex 同時匹配可能過於嚴格</summary>

將原本的 `Assert.Matches` 改為同時檢查新舊兩個 Regex，但錯誤訊息可能只符合其中一種模式。若瀏覽器版本不同，可能導致測試不穩定。建議使用 `Assert.True` 搭配 OR 條件，或使用 `Assert.Matches` 逐一檢查。

**判斷依據**：diff 顯示原本的 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 改為同時檢查兩個 Regex 的 AND 條件。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8709 (cache hit 8704) ｜ completion tokens 1056 ｜ PR #2</sub>