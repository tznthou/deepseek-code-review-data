<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為多個專案更新 XML 文件註解，使其更符合 .NET 文件規範（如加入 <value>、<remarks> 標籤、調整用詞）。大部分變更僅影響文件，無功能變動。然而，有兩處程式碼邏輯變更需特別注意：AzureFileLoggerOptions.RetainedFileCountLimit 的驗證條件從 `value <= 0` 改為 `value < 0`，可能允許 0 值，與文件描述「strictly positive」矛盾；BatchingLoggerOptions.BackgroundQueueSize 的驗證從 `value < 0` 改為 `value <= 0`，可能禁止 0 值，但錯誤訊息仍為「must be non-negative」，且文件未明確說明 0 的意義。建議先確認這些變更的意圖並修正文件或驗證邏輯。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53` | RetainedFileCountLimit 驗證條件變更可能允許 0 值 | 0.80 |
| ⚠️ | Major | `src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:44` | BackgroundQueueSize 驗證條件變更可能禁止 0 值 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53</code> RetainedFileCountLimit 驗證條件變更可能允許 0 值</summary>

驗證條件從 `value <= 0` 改為 `value < 0`，這表示 `value = 0` 現在會被接受。但屬性文件仍描述為「strictly positive value」，且錯誤訊息仍為「must be positive」。若 0 值被允許，可能導致保留檔案數為 0 的意外行為（例如不保留任何檔案），或與其他邏輯衝突。請確認此變更是否為預期，並更新文件與錯誤訊息以反映實際允許的範圍。

**判斷依據**：diff 中此行由 `if (value <= 0)` 改為 `if (value < 0)`，但文件與錯誤訊息未同步更新。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:44</code> BackgroundQueueSize 驗證條件變更可能禁止 0 值</summary>

驗證條件從 `value < 0` 改為 `value <= 0`，這表示 `value = 0` 現在會拋出例外。但錯誤訊息仍為「must be non-negative」，且文件未明確說明 0 的意義（可能代表無佇列或無限制）。若 0 值原本是合法設定，此變更會破壞向後相容性。請確認意圖並更新文件與錯誤訊息。

**判斷依據**：diff 中此行由 `if (value < 0)` 改為 `if (value <= 0)`，但錯誤訊息仍為「must be non-negative」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11854 (cache hit 1536) ｜ completion tokens 704 ｜ PR #10</sub>