<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為文件註解更新，並包含兩處程式碼變更：AzureFileLoggerOptions.RetainedFileCountLimit 的驗證條件從 `value <= 0` 改為 `value < 0`，以及 BatchingLoggerOptions.BackgroundQueueSize 的驗證條件從 `value < 0` 改為 `value <= 0`。這兩處變更可能改變屬性設定時的行為，需確認是否為預期修正。其餘變更為文件格式調整，風險低。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53` | RetainedFileCountLimit 驗證條件變更可能允許零值 | 0.90 |
| ⚠️ | Major | `src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47` | BackgroundQueueSize 驗證條件變更可能拒絕零值 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53</code> RetainedFileCountLimit 驗證條件變更可能允許零值</summary>

原本 `value <= 0` 會拒絕零和負數，現在改為 `value < 0` 只拒絕負數，允許零。若零值被接受，可能導致保留檔案數為零，造成所有日誌檔案被刪除或無法保留任何檔案，影響日誌留存。建議確認此變更是否為預期行為，若非預期應改回 `value <= 0`。

**判斷依據**：diff 中此行由 `if (value <= 0)` 改為 `if (value < 0)`，且錯誤訊息仍為 "must be positive"，與允許零值矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47</code> BackgroundQueueSize 驗證條件變更可能拒絕零值</summary>

原本 `value < 0` 允許零值（代表無限制），現在改為 `value <= 0` 會拒絕零值。若零值原本表示無限制，此變更將導致設定零值時拋出例外，可能破壞現有使用者的設定。建議確認零值是否應被允許，若應允許則改回 `value < 0`。

**判斷依據**：diff 中此行由 `if (value < 0)` 改為 `if (value <= 0)`，且錯誤訊息仍為 "must be non-negative"，與拒絕零值矛盾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9117 (cache hit 9088) ｜ completion tokens 596 ｜ PR #10</sub>