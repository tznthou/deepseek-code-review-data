<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本（9.0.0-beta.25562.4 → 9.0.0-beta.25626.6），並包含多項建置與測試基礎架構的調整：Azure Linux 3 映像、source-index 條件、內部 feed URL、PowerShell 相容性修正、vswhere 處理、WebSocket 壓縮測試的 CSP 錯誤訊息正規化、Redis 測試隔離與 WebSocketWrapper 修正。整體風險中等，需注意依賴版本跳躍可能引入行為變更，以及測試隔離可能掩蓋真實問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92` | 新增 QuarantinedTest 可能掩蓋真實回歸 | 0.80 |
| ⚠️ | Major | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188` | 新增 QuarantinedTest 可能掩蓋真實回歸 | 0.80 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409` | WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設時機變更可能影響後續讀取 | 0.70 |
| 🔸 | Minor | `eng/common/tools.ps1:550` | vswhere 需求處理可能遺漏必要元件 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92</code> 新增 QuarantinedTest 可能掩蓋真實回歸</summary>

在 `CanSendAndReceiveUserMessagesFromMultipleConnectionsWithSameUser` 測試上新增 `[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/59991")]`，表示該測試已知不穩定而被隔離。隔離測試會降低 CI 對真實回歸的敏感度，若問題根源未解決，可能導致相關功能在未來被破壞而無人察覺。建議確認 issue #59991 的狀態，並在修復後移除隔離屬性。

**判斷依據**：diff 中新增的屬性行，位於測試方法上方。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188</code> 新增 QuarantinedTest 可能掩蓋真實回歸</summary>

在 `CanSendAndReceiveUserMessagesUserNameWithPatternIsTreatedAsLiteral` 測試上新增 `[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/63582")]`，表示該測試已知不穩定而被隔離。隔離測試會降低 CI 對真實回歸的敏感度，若問題根源未解決，可能導致相關功能在未來被破壞而無人察覺。建議確認 issue #63582 的狀態，並在修復後移除隔離屬性。

**判斷依據**：diff 中新增的屬性行，位於測試方法上方。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409</code> WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設時機變更可能影響後續讀取</summary>

將 `_receiveTcs = new(...)` 從零位元組讀取處理之後移到之前，確保每次呼叫 `ReceiveAsync` 都會建立新的 TaskCompletionSource。這修正了先前在零位元組讀取時未重設 `_receiveTcs` 的潛在問題，但需確認此變更不會影響連續讀取的語意。建議檢視相關測試是否涵蓋零位元組讀取情境。

**判斷依據**：diff 中移動的行，從原本在零位元組處理之後移到之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>eng/common/tools.ps1:550</code> vswhere 需求處理可能遺漏必要元件</summary>

當 `$GlobalJson.tools` 不存在 `vs` 屬性時，將 `$vsRequirements` 設為 `$null`，後續 `Get-Member` 檢查會跳過版本和元件參數。這可能導致在沒有指定 VS 需求的環境中，無法正確找到 Visual Studio。建議確認此變更符合預期，並考慮提供預設需求。

**判斷依據**：diff 中新增的條件判斷區塊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6524 (cache hit 6400) ｜ completion tokens 1138 ｜ PR #2</sub>