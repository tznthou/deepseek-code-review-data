<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本（9.0.0-beta.25562.4 → 9.0.0-beta.25626.6），並包含多項基礎架構調整：將內部映像從 Mariner 2 改為 Azure Linux 3、更新內部套件來源 URL、在 PowerShell 的 Invoke-WebRequest 中加入 -UseBasicParsing、修正 vswhere 需求處理、調整 WebSocket 測試的錯誤訊息比對、將兩個 Redis 測試標記為隔離，以及修正 WebSocketWrapper 的接收邏輯。整體風險中等，主要疑慮在於 WebSocketWrapper 的變更可能影響測試行為，以及依賴版本更新可能引入未預期的行為變更。建議確認相關測試通過後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409` | WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重置時機變更可能導致測試行為不正確 | 0.80 |
| 🔸 | Minor | `eng/common/tools.ps1:550` | vswhere 需求處理變更可能導致 $vsRequirements 為 null 時行為不一致 | 0.70 |
| 🔸 | Minor | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 錯誤訊息比對同時要求符合新舊兩種正規表達式，可能過於嚴格 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409</code> WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重置時機變更可能導致測試行為不正確</summary>

原本在處理完 buffer 後才重置 _receiveTcs，現在改為在 await 後立即重置。這可能導致在 buffer.Count == 0 的 zero-byte read 情況下，下一次呼叫 ReceiveAsync 時會 await 一個新的 TaskCompletionSource，而該 TCS 尚未被設定，造成測試卡住或行為不符預期。建議確認此變更是否為修正特定問題，並確保所有相關測試（包括 zero-byte read 情境）通過。

**判斷依據**：diff 顯示 _receiveTcs 的重置從 buffer.Count == 0 的 early return 之後移到 await 之後，改變了 zero-byte read 時的行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/tools.ps1:550</code> vswhere 需求處理變更可能導致 $vsRequirements 為 null 時行為不一致</summary>

當 $GlobalJson.tools 沒有 'vs' 屬性時，$vsRequirements 被設為 $null，後續的 Get-Member 檢查也增加了 $vsRequirements 的 null 檢查。但原本的程式碼在 $vsRequirements 為 null 時會直接使用 $GlobalJson.tools.vs（可能也是 null），行為可能相同。建議確認此變更是否為修正特定問題，並確保在各種 global.json 設定下行為正確。

**判斷依據**：diff 顯示原本直接指派 $GlobalJson.tools.vs，現在改為條件指派並可能設為 null。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 錯誤訊息比對同時要求符合新舊兩種正規表達式，可能過於嚴格</summary>

測試現在要求 log 訊息同時符合 ParseErrorMessageRegexOld 和 ParseErrorMessageRegexNew。若瀏覽器或執行環境只產生其中一種格式，測試將失敗。建議確認兩種格式是否可能同時出現，或改為符合其中一種即可。

**判斷依據**：diff 顯示原本使用 Assert.Matches(ParseErrorMessage(), logs[0].Message)，現在改為同時檢查兩個 regex。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8699 (cache hit 6400) ｜ completion tokens 1009 ｜ PR #2</sub>