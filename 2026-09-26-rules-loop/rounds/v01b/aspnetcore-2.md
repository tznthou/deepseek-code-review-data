<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項建置與測試基礎架構的調整。主要風險在於 `WebSocketCompressionTests.cs` 中斷言邏輯的變更：原本應符合單一錯誤訊息格式，現在改為同時符合新舊兩種格式，這可能掩蓋實際的 CSP 錯誤。此外，`source-index-stage1.yml` 的 condition 變更可能導致非 main 分支的來源索引被略過，需確認是否符合預期。整體而言，變更範圍明確，但建議釐清上述兩點。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 斷言邏輯變更可能掩蓋 CSP 錯誤 | 0.80 |
| ⚠️ | Major | `eng/common/core-templates/job/source-index-stage1.yml:9` | 來源索引條件變更可能影響非 main 分支 | 0.70 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92` | 新增 QuarantinedTest 屬性可能隱藏測試失敗 | 0.60 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213` | DisposeAsync 順序變更可能影響資源釋放 | 0.50 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408` | ReceiveAsync 中 _receiveTcs 重置位置變更可能影響並行 | 0.50 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362` | 移除 sealed 關鍵字可能違反專案規範 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 斷言邏輯變更可能掩蓋 CSP 錯誤</summary>

原本測試預期日誌訊息符合單一正規表達式 `ParseErrorMessage()`，現在改為同時符合 `ParseErrorMessageRegexOld` 和 `ParseErrorMessageRegexNew`。這可能導致測試永遠失敗，因為單一訊息不可能同時符合兩種格式；或者若兩種格式都可能出現，則應使用 OR 條件而非 AND。請確認實際預期的錯誤訊息格式，並修正斷言邏輯。

**判斷依據**：diff 中新增的 Assert.True 使用 && 運算子同時檢查兩個 regex，但錯誤訊息不可能同時符合兩種格式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>eng/common/core-templates/job/source-index-stage1.yml:9</code> 來源索引條件變更可能影響非 main 分支</summary>

原本 condition 為空字串（表示永遠執行），現在改為 `eq(variables['Build.SourceBranch'], 'refs/heads/main')`。這會導致在 release 分支或其他分支上，來源索引階段被略過。若來源索引用於符號伺服器或來源連結，這可能影響除錯體驗。請確認此變更是否符合預期。

**判斷依據**：diff 中 condition 從空字串改為特定分支條件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92</code> 新增 QuarantinedTest 屬性可能隱藏測試失敗</summary>

在兩個測試方法上新增 `[QuarantinedTest]` 屬性，這會將測試標記為隔離，可能導致 CI 中跳過或延遲報告失敗。請確認這些測試確實不穩定，並有追蹤修復的 issue。

**判斷依據**：diff 中新增 QuarantinedTest 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:213</code> DisposeAsync 順序變更可能影響資源釋放</summary>

原本先釋放 `connection` 再釋放 `secondConnection`，現在順序相反。若兩個連線有相依性，可能導致釋放時發生例外或資源洩漏。請確認此變更的必要性。

**判斷依據**：diff 中 DisposeAsync 呼叫順序對調。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408</code> ReceiveAsync 中 _receiveTcs 重置位置變更可能影響並行</summary>

原本在複製資料後才重置 `_receiveTcs`，現在改為在 await 後立即重置。若有多個並行 ReceiveAsync 呼叫，可能導致競爭條件。請確認此變更的執行緒安全性。

**判斷依據**：diff 中 _receiveTcs 重置位置從複製後移至 await 後。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:362</code> 移除 sealed 關鍵字可能違反專案規範</summary>

`WebSocketWrapper` 類別從 `internal sealed class` 改為 `internal class`，可能違反專案規範 R14（內部實作類別應為 sealed）。若此類別不預期被繼承，建議保留 sealed。

**判斷依據**：diff 中移除 sealed 關鍵字。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8709 (cache hit 8704) ｜ completion tokens 1382 ｜ PR #2</sub>