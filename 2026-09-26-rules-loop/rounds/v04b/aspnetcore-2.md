<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項建置腳本與測試的調整。主要風險在於 WebSocketCompressionTests 的斷言邏輯變更可能導致測試永遠通過，以及 WebSocketWrapper 中 _receiveTcs 重置時機的變更可能引入競態條件。建議優先修正這兩個問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 測試斷言邏輯錯誤：使用 AND 條件導致測試永遠通過 | 0.95 |
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408` | WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重置時機可能導致競態條件 | 0.80 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362` | [R14] 內部類別 WebSocketWrapper 未標記為 sealed | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 測試斷言邏輯錯誤：使用 AND 條件導致測試永遠通過</summary>

原本的 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 改為 `Assert.True(ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ...)`。這兩個 regex 分別對應舊版與新版的錯誤訊息格式，但同一筆 log 不可能同時符合兩種格式，因此 `&&` 條件永遠為 false，測試將永遠失敗。應改為 `||` 條件，或使用 `Assert.Matches` 搭配單一 regex 來涵蓋兩種格式。

**判斷依據**：diff 中新增的 `Assert.True` 使用了 `&&` 運算子，但兩個 regex 分別對應不同的錯誤訊息格式，邏輯上不可能同時成立。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408</code> WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重置時機可能導致競態條件</summary>

原本在複製資料後才重置 `_receiveTcs`，現在改為在 await 之後立即重置。若在 `res.Item2.CopyTo(buffer)` 執行期間有其他執行緒呼叫 `SetReceiveResult`，新的結果會被寫入新的 `_receiveTcs`，但目前的複製仍使用舊的 `res`，可能導致資料不一致或遺失。建議保持原本的順序，在複製完成後再重置。

**判斷依據**：diff 中將 `_receiveTcs = new(...)` 從 `res.Item2.CopyTo(buffer)` 之後移到之前，可能導致並行存取問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362</code> [R14] 內部類別 WebSocketWrapper 未標記為 sealed</summary>

根據規範 R14，內部實作類別應標記為 `sealed` 以提升效能並明確設計意圖。此類別原本為 `internal sealed class`，但此次變更移除了 `sealed` 修飾詞。

**判斷依據**：diff 中將 `internal sealed class WebSocketWrapper` 改為 `internal class WebSocketWrapper`，違反 R14。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7474 (cache hit 7424) ｜ completion tokens 949 ｜ PR #2</sub>