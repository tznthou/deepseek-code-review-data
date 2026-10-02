<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新多個專案的 XML 文件註解，使其符合 .NET 文件規範（如加入 <value>、<remarks>、<see langword> 等標籤），並調整部分用語。同時包含兩處程式碼變更：AzureFileLoggerOptions.RetainedFileCountLimit 的驗證條件從 `value <= 0` 改為 `value < 0`，以及 BatchingLoggerOptions.BackgroundQueueSize 的驗證條件從 `value < 0` 改為 `value <= 0`。前者允許 0 值，可能導致保留檔案數為 0 的意外行為；後者禁止 0 值，但錯誤訊息仍為「must be non-negative」，不一致。整體風險低，但建議修正驗證邏輯與訊息。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53` | RetainedFileCountLimit 允許 0 可能導致非預期行為 | 0.80 |
| 🔸 | Minor | `src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:45` | BackgroundQueueSize 驗證條件與錯誤訊息不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53</code> RetainedFileCountLimit 允許 0 可能導致非預期行為</summary>

驗證條件從 `value <= 0` 改為 `value < 0`，允許設定為 0。若設為 0，可能導致不保留任何檔案，或與預期的「無限制」語意混淆。建議確認 0 是否為有效值，若否，應維持 `value <= 0` 並更新錯誤訊息。

**判斷依據**：diff 中此行由 `if (value <= 0)` 改為 `if (value < 0)`，且錯誤訊息仍為「must be positive」，與允許 0 矛盾。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:45</code> BackgroundQueueSize 驗證條件與錯誤訊息不一致</summary>

驗證條件從 `value < 0` 改為 `value <= 0`，禁止 0 值，但錯誤訊息仍為「must be non-negative」，與條件矛盾。建議更新錯誤訊息為「must be positive」或調整條件。

**判斷依據**：diff 中此行由 `if (value < 0)` 改為 `if (value <= 0)`，但錯誤訊息未同步更新。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11854 (cache hit 11776) ｜ completion tokens 608 ｜ PR #10</sub>