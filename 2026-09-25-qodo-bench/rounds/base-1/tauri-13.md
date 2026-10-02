<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的版本更新，主要將多個 crate 從 2.9.0/2.5.0/2.7.0/2.2.0 升級至 2.9.1/2.5.1/2.7.1/2.3.0，並包含 tauri-macos-sign 的錯誤處理重構（從 thiserror 改為手動實作 Display 與 Error trait）。整體風險集中在 tauri-macos-sign 的邏輯變更：`notarize_inner` 中 `map_or` 的參數從 `!wait` 改為 `wait`，以及 `ditto` 命令參數順序調整。前者可能改變非同步 notarization 的行為，後者需確認 ditto 的參數順序是否正確。此外，錯誤處理重構移除了 thiserror 的自動來源追蹤，需確保手動實作的 `source()` 方法涵蓋所有應有欄位。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 中 map_or 的條件邏輯可能反轉 | 0.80 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | ditto 命令參數順序調整可能影響行為 | 0.60 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:80` | 手動實作 Error trait 可能遺漏 source 方法 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 中 map_or 的條件邏輯可能反轉</summary>

在 `notarize_inner` 函式中，原本的 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 被改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。

此變更會影響當 `status` 為 `None` 時的行為：
- 舊邏輯：若 `wait` 為 false，則 `map_or` 回傳 true（因為 `!wait`），因此會進入 if 區塊並印出 "Notarizing" 訊息。
- 新邏輯：若 `wait` 為 false，則 `map_or` 回傳 false，因此不會進入 if 區塊。

這可能導致在非等待模式下，即使 notarization 尚未完成，也不會印出 "Notarizing" 訊息，進而影響使用者體驗或後續流程。

建議確認此變更是否為預期行為，並考慮是否應保留原邏輯或調整條件。

**判斷依據**：diff 中顯示此行從 `if submit_output.status.map_or(!wait, |s| s == "Accepted") {` 改為 `if submit_output.status.map_or(wait, |s| s == "Accepted") {`，邏輯明顯反轉。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> ditto 命令參數順序調整可能影響行為</summary>

在 `notarize_inner` 中，`ditto` 命令的參數順序從原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。

需要確認 `ditto` 命令的參數順序是否正確：`ditto` 的語法為 `ditto [options] source destination`，因此 source 應為 `app_bundle_path`，destination 應為 `zip_path`。若順序顛倒，可能導致壓縮錯誤或失敗。

建議驗證此變更是否為修正或意外。

**判斷依據**：diff 中顯示參數順序從 `app_bundle_path` 在前改為 `zip_path` 在前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:80</code> 手動實作 Error trait 可能遺漏 source 方法</summary>

錯誤處理從 `thiserror::Error` 改為手動實作 `Display` 和 `Error` trait。在 `source()` 方法中，僅對 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 回傳來源錯誤，但其他 variant（如 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER`）也包含錯誤欄位，卻未回傳其來源。

這可能導致使用 `anyhow` 或 `eyre` 等 crate 時，無法取得完整的錯誤鏈。建議為所有包含錯誤欄位的 variant 實作 `source()`。

**判斷依據**：diff 中新增的 `source()` 方法僅處理部分 variant。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10605 (cache hit 1536) ｜ completion tokens 1329 ｜ PR #13</sub>