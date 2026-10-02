<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要包含 tauri-macos-sign 的錯誤型別重構（從 thiserror 改為手動實作 Display/Error），以及相依套件版本號提升。整體風險集中在 tauri-macos-sign 的錯誤處理變更：手動實作可能遺漏 source() 或 Display 格式不一致，且 notarize_inner 中 wait 參數的邏輯反轉可能影響行為。建議確認錯誤處理的正確性與測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:80` | Error::source() 未涵蓋所有可提供來源的變體 | 0.80 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 中 wait 參數的邏輯可能反轉 | 0.75 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:64` | Display 實作與原本 thiserror 格式不完全一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:80</code> Error::source() 未涵蓋所有可提供來源的變體</summary>

手動實作的 `source()` 僅回傳 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 的底層錯誤，但 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER` 等變體也包含底層錯誤，卻未回傳。這會讓使用 `Error::source()` 的錯誤鏈走訪中斷，影響錯誤診斷。建議為所有包含底層錯誤的變體實作 `source()`。

**判斷依據**：diff 中新增的 `source()` 實作只處理四個變體，但 `Error` 列舉中 `Plist { error: plist::Error }`、`X509Certificate { error: x509_certificate::X509CertificateError }`、`FailedToCreateSelfSignedCertificate { error: Box<apple_codesign::AppleCodesignError> }`、`FailedToEncodeDER { error: std::io::Error }` 也包含底層錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 中 wait 參數的邏輯可能反轉</summary>

原本 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 在 `wait` 為 false 時，若 status 為 None 會進入成功分支；改為 `map_or(wait, ...)` 後，`wait` 為 false 且 status 為 None 時會進入失敗分支。這可能導致非等待模式下，若 notarytool 未回傳 status（例如剛提交尚未有狀態），程式會誤判為失敗。請確認此變更是否為預期行為。

**判斷依據**：diff 中此行由 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`，邏輯相反。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:64</code> Display 實作與原本 thiserror 格式不完全一致</summary>

原本 `thiserror` 的 `#[error("{context} {path}: {error}")]` 會直接使用 `path` 的 Display，但手動實作改為 `path.display()`，兩者輸出可能不同（例如 `PathBuf` 的 Display 與 `path.display()` 通常相同，但若 path 包含非 UTF-8 字元，`display()` 會使用替代字元）。建議確認是否可接受。

**判斷依據**：diff 中 `Plist` 的 Display 實作使用 `path.display()`，而原本 thiserror 的格式為 `{path}`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11458 (cache hit 1536) ｜ completion tokens 1065 ｜ PR #13</sub>