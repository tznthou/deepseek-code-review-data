<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的版本更新，主要包含版本號提升、依賴升級、錯誤型別重構（tauri-macos-sign 的 Error 改為自訂 Display/Error 實作）以及 notarize_inner 中的條件邏輯修正。整體風險中等：錯誤型別重構移除了 thiserror 衍生，改為手動實作，需確認是否符合專案規範 R08；notarize_inner 的條件反轉可能影響非等待模式下的行為，需驗證；其餘多為版本與依賴更新，風險較低。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R08] 錯誤型別未使用 thiserror，改為手動實作 Display 與 Error | 0.80 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件邏輯反轉可能導致非等待模式行為錯誤 | 0.75 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | 參數順序調整可能影響命令列參數的語意 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R08] 錯誤型別未使用 thiserror，改為手動實作 Display 與 Error</summary>

此變更將原本使用 `#[derive(Debug, thiserror::Error)]` 的 `Error` 列舉改為僅 `#[derive(Debug)]`，並手動實作 `Display` 與 `std::error::Error`。這違反了專案規範 R08（錯誤型別應使用 thiserror）。手動實作可能導致錯誤訊息不一致、增加維護成本，且容易在新增變體時遺漏更新。建議改回使用 `thiserror::Error` 衍生，並保留原有的 `#[error(...)]` 屬性。

**判斷依據**：diff 中移除了 `#[derive(Debug, thiserror::Error)]` 及所有 `#[error(...)]` 屬性，並新增了 `impl std::fmt::Display for Error` 與 `impl std::error::Error for Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件邏輯反轉可能導致非等待模式行為錯誤</summary>

原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。此變更反轉了當 `status` 為 `None` 時的預設值：原本 `!wait`（非等待時為 true），現在改為 `wait`（等待時為 true）。這可能導致在非等待模式下（`wait == false`）即使沒有狀態也不會進入後續的列印與處理邏輯，或在等待模式下（`wait == true`）即使沒有狀態也會進入，造成行為錯誤。需確認此變更的意圖與正確性。

**判斷依據**：diff 中該行由 `if submit_output.status.map_or(!wait, |s| s == "Accepted") {` 改為 `if submit_output.status.map_or(wait, |s| s == "Accepted") {`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> 參數順序調整可能影響命令列參數的語意</summary>

在 `notarize_inner` 中，`app_bundle_path` 與 `zip_path` 的參數順序被調換。雖然兩者皆為路徑，但若命令列工具對參數位置有特定要求，可能導致錯誤。需確認 `ditto` 或相關命令的參數順序是否正確。

**判斷依據**：diff 中原本 `app_bundle_path` 在前，`zip_path` 在後，現在順序對調。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12697 (cache hit 10496) ｜ completion tokens 1279 ｜ PR #13</sub>