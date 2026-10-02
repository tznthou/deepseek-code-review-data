<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為文件註解更新，但包含兩處行為變更：AzureFileLoggerOptions.RetainedFileCountLimit 的驗證條件從 `value <= 0` 改為 `value < 0`，以及 BatchingLoggerOptions.BackgroundQueueSize 的驗證條件從 `value < 0` 改為 `value <= 0`。前者允許 0 值，可能導致保留檔案數為 0 的意外行為；後者禁止 0 值，可能破壞原本允許 0 的合法使用情境。建議確認這些變更是否符合預期，並補充對應的測試。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53` | RetainedFileCountLimit 驗證條件變更可能允許 0 值 | 0.85 |
| ⚠️ | Major | `src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47` | BackgroundQueueSize 驗證條件變更可能禁止 0 值 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53</code> RetainedFileCountLimit 驗證條件變更可能允許 0 值</summary>

原本的驗證條件 `value <= 0` 會拒絕 0 和負數，但變更後只拒絕負數，允許 0。若設定為 0，可能導致不保留任何檔案，造成資料遺失或非預期行為。建議確認 0 是否為有效值，若不是，應維持原本的 `<= 0` 驗證。

**判斷依據**：diff 中此行由 `if (value <= 0)` 改為 `if (value < 0)`，且錯誤訊息仍為 "must be positive"，顯示 0 不應被允許。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47</code> BackgroundQueueSize 驗證條件變更可能禁止 0 值</summary>

原本的驗證條件 `value < 0` 允許 0（表示無佇列），但變更後 `value <= 0` 會拒絕 0。若原本有使用者設定 0 來停用佇列，此變更將導致例外。建議確認 0 是否為有效值，若不是，應更新文件說明；若是，應維持原本的驗證。

**判斷依據**：diff 中此行由 `if (value < 0)` 改為 `if (value <= 0)`，且錯誤訊息仍為 "must be non-negative"，顯示 0 應被允許。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9117 (cache hit 1408) ｜ completion tokens 624 ｜ PR #10</sub>