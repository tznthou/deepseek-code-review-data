<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本（9.0.0-beta.25562.4 → 9.0.0-beta.25626.6），並包含多項建置腳本與測試的調整。主要風險在於 WebSocketCompressionTests 中正規表達式驗證邏輯的變更，可能因瀏覽器錯誤訊息格式不同而導致測試不穩定；此外，RedisEndToEnd 測試新增隔離標記，暗示已知不穩定問題。整體變更範圍明確，但需注意測試可靠性與依賴升級的相容性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 正規表達式驗證邏輯可能導致測試不穩定 | 0.80 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92` | 新增隔離標記可能掩蓋潛在問題 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188` | 新增隔離標記可能掩蓋潛在問題 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213` | DisposeAsync 順序變更可能影響測試穩定性 | 0.60 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409` | WebSocketWrapper 中 _receiveTcs 重置時機變更可能影響並發 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 正規表達式驗證邏輯可能導致測試不穩定</summary>

原本使用單一正規表達式 `ParseErrorMessage()` 驗證日誌訊息，現在改為同時檢查 `ParseErrorMessageRegexOld` 和 `ParseErrorMessageRegexNew` 兩個模式。這可能導致測試在瀏覽器錯誤訊息格式略有變化時失敗，因為兩個模式都必須匹配。建議改為使用 `Assert.Matches` 搭配單一正規表達式，或使用 `Assert.True` 檢查任一模式匹配，以提高測試穩定性。

**判斷依據**：diff 中將原本的 `Assert.Matches(ParseErrorMessage(), logs[0].Message);` 改為同時檢查兩個正規表達式，且錯誤訊息指出「Expected log message to match one of the CSP error patterns」，但程式碼卻要求兩個都匹配，邏輯不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92</code> 新增隔離標記可能掩蓋潛在問題</summary>

在 `CanSendAndReceiveUserMessagesFromMultipleConnectionsWithSameUser` 測試方法上新增 `[QuarantinedTest]` 屬性，表示該測試已知不穩定。雖然隔離可以減少 CI 干擾，但應確保有對應的 issue 追蹤修復，並定期檢視是否可移除隔離。

**判斷依據**：diff 中新增了 `[QuarantinedTest]` 屬性，並附上 issue 連結。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188</code> 新增隔離標記可能掩蓋潛在問題</summary>

在 `CanSendAndReceiveUserMessagesUserNameWithPatternIsTreatedAsLiteral` 測試方法上新增 `[QuarantinedTest]` 屬性，表示該測試已知不穩定。雖然隔離可以減少 CI 干擾，但應確保有對應的 issue 追蹤修復，並定期檢視是否可移除隔離。

**判斷依據**：diff 中新增了 `[QuarantinedTest]` 屬性，並附上 issue 連結。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213</code> DisposeAsync 順序變更可能影響測試穩定性</summary>

原本先 `connection.DisposeAsync()` 再 `secondConnection.DisposeAsync()`，現在順序對調。雖然通常不影響功能，但若連線之間有相依性，可能導致測試行為改變。建議確認此變更的必要性。

**判斷依據**：diff 中將兩行順序對調。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409</code> WebSocketWrapper 中 _receiveTcs 重置時機變更可能影響並發</summary>

原本在處理完接收結果後才重置 `_receiveTcs`，現在改為在 await 之後立即重置。這可能導致在處理零位元組讀取時，下一次接收會使用新的 TCS，但若有多個並發接收，可能造成競態。建議確認此變更是否為了解決特定問題，並評估並發安全性。

**判斷依據**：diff 中將 `_receiveTcs = new(...)` 從原本的位置移到 await 之後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7474 (cache hit 6400) ｜ completion tokens 1325 ｜ PR #2</sub>