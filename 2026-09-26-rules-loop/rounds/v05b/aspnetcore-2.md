<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 相依套件版本，並包含數個建置管線與測試的調整。主要風險在於 `WebSocketCompressionTests.cs` 中 CSP 錯誤訊息的比對邏輯變更，以及 `RedisEndToEnd.cs` 中測試隔離與 WebSocket 包裝器的修改。整體變更範圍不大，但需確認測試邏輯的正確性與相容性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | CSP 錯誤訊息比對邏輯可能過於嚴格 | 0.80 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92` | 新增 QuarantinedTest 屬性可能隱藏測試失敗 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213` | DisposeAsync 順序變更可能影響測試穩定性 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362` | WebSocketWrapper 類別移除 sealed 修飾詞 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409` | ReceiveAsync 中 _receiveTcs 重設位置變更可能影響行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> CSP 錯誤訊息比對邏輯可能過於嚴格</summary>

原本使用單一 Regex 比對，現在改為同時比對兩個 Regex（`ParseErrorMessageRegexOld` 與 `ParseErrorMessageRegexNew`）。若瀏覽器版本或錯誤訊息格式略有不同，可能導致測試失敗。建議確認兩個 Regex 是否涵蓋所有可能的錯誤訊息格式，或考慮使用單一更寬鬆的 Regex。

**判斷依據**：diff 中新增了第二個 Regex 並要求兩者同時匹配，但錯誤訊息可能因瀏覽器而異，導致測試不穩定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92</code> 新增 QuarantinedTest 屬性可能隱藏測試失敗</summary>

在兩個測試方法上新增 `[QuarantinedTest]` 屬性，這會將測試標記為隔離，可能導致 CI 忽略其失敗。請確認這些測試確實不穩定，並有對應的 issue 追蹤修復。

**判斷依據**：diff 中新增了 QuarantinedTest 屬性，但未提供測試不穩定的具體原因。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213</code> DisposeAsync 順序變更可能影響測試穩定性</summary>

將 `connection.DisposeAsync()` 移到 `secondConnection.DisposeAsync()` 之後，可能改變資源釋放順序，導致測試行為變化。請確認此變更是否為修正特定問題，並確保不會引入新的不穩定。

**判斷依據**：diff 中調整了 DisposeAsync 的呼叫順序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362</code> WebSocketWrapper 類別移除 sealed 修飾詞</summary>

將 `internal sealed class WebSocketWrapper` 改為 `internal class WebSocketWrapper`，可能違反專案規範 [R14]（內部實作類別應為 sealed）。請確認是否有繼承需求，否則應保留 sealed。

**判斷依據**：diff 中移除了 sealed 關鍵字。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409</code> ReceiveAsync 中 _receiveTcs 重設位置變更可能影響行為</summary>

將 `_receiveTcs = new(...)` 移到 `if (buffer.Count == 0)` 之前，可能改變零位元組讀取時的行為。請確認此變更是否為修正特定問題，並確保不會引入新的錯誤。

**判斷依據**：diff 中調整了 _receiveTcs 重設的位置。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8643 (cache hit 8576) ｜ completion tokens 1159 ｜ PR #2</sub>