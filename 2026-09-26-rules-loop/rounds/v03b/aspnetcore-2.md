<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項建置腳本與測試的調整。整體風險中等：依賴版本更新需確保與專案相容；測試程式碼的變更（如 WebSocketCompressionTests 的 regex 調整、RedisEndToEnd 的隔離標記）需驗證其正確性。最需優先確認的是 WebSocketCompressionTests 中新的斷言邏輯是否正確涵蓋所有預期的錯誤訊息格式，以及 RedisEndToEnd 中 WebSocketWrapper 的變更是否會影響測試行為。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 斷言邏輯可能過於嚴格，導致測試不穩定 | 0.80 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92` | 新增隔離標記但未提供詳細說明 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188` | 新增隔離標記但未提供詳細說明 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213` | DisposeAsync 順序變更可能影響測試清理 | 0.60 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362` | 移除 sealed 修飾詞可能違反專案規範 | 0.60 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408` | ReceiveAsync 中 _receiveTcs 重置時機變更可能影響並行行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 斷言邏輯可能過於嚴格，導致測試不穩定</summary>

原本的斷言 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 只要求符合單一 regex。現在改為要求同時符合 `ParseErrorMessageRegexOld` 和 `ParseErrorMessageRegexNew` 兩個 regex。這兩個 regex 分別對應不同的錯誤訊息格式（'Refused to frame' vs 'Framing'），實際上同一則日誌不可能同時符合兩者。因此，此斷言永遠不會通過，除非 `logs[0].Message` 同時包含兩種模式（不太可能）。建議改為使用 `Assert.True(ParseErrorMessageRegexOld.IsMatch(...) || ParseErrorMessageRegexNew.IsMatch(...))`，或使用 `Assert.Matches` 搭配一個合併的 regex。

**判斷依據**：diff 中新增的斷言使用 `&&` 運算子，要求兩個 regex 都必須匹配。但兩個 regex 的 pattern 互斥（'Refused to frame' vs 'Framing'），因此不可能同時匹配。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92</code> 新增隔離標記但未提供詳細說明</summary>

新增 `[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/59991")]` 屬性，將測試標記為隔離。這通常表示測試不穩定或已知失敗。建議在 PR 描述或程式碼註解中說明隔離原因，並確認 issue 連結有效。

**判斷依據**：diff 中新增的屬性行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188</code> 新增隔離標記但未提供詳細說明</summary>

新增 `[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/63582")]` 屬性，將測試標記為隔離。這通常表示測試不穩定或已知失敗。建議在 PR 描述或程式碼註解中說明隔離原因，並確認 issue 連結有效。

**判斷依據**：diff 中新增的屬性行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213</code> DisposeAsync 順序變更可能影響測試清理</summary>

原本先 `connection.DisposeAsync()` 再 `secondConnection.DisposeAsync()`，現在順序對調。若兩個連線有相依性（例如共用資源），順序變更可能導致清理不完整或例外。建議確認此變更的必要性，並確保測試仍能正確清理資源。

**判斷依據**：diff 中兩行順序對調。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362</code> 移除 sealed 修飾詞可能違反專案規範</summary>

`WebSocketWrapper` 類別從 `internal sealed class` 改為 `internal class`。根據專案規範 R14，內部實作類別應標記為 sealed，除非明確設計為繼承。此變更可能違反規範，且若無繼承需求，建議保留 sealed。

**判斷依據**：diff 中移除 sealed 關鍵字。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408</code> ReceiveAsync 中 _receiveTcs 重置時機變更可能影響並行行為</summary>

原本在處理完 buffer 後才重置 `_receiveTcs`，現在改為在 await 後立即重置。這可能導致在處理 buffer 期間，若有其他執行緒嘗試設定新的接收結果，會覆蓋尚未使用的 `_receiveTcs`，造成資料遺失或競態。建議確認此變更是否為了解決特定問題，並評估並行安全性。

**判斷依據**：diff 中 `_receiveTcs = new(...)` 從 if 區塊後移至 await 後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8719 (cache hit 8704) ｜ completion tokens 1581 ｜ PR #2</sub>