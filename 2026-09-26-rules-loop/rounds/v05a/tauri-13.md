<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的版本更新，主要包含：多個 crate 的 patch/minor 版本號提升、tauri-macos-sign 的 Error 型別從 thiserror 改為手動實作 Display/Error、以及 notarize_inner 中的引數順序與條件邏輯修正。整體風險中等，需特別注意 Error 型別變更是否符合專案規範（R08/R09）以及 notarize_inner 的邏輯變更是否正確。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R08] 自訂 Error 型別未使用 thiserror，違反專案規範 | 0.90 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開 Error 列舉未標記 #[non_exhaustive] | 0.85 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件邏輯變更可能導致行為錯誤 | 0.80 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | 引數順序變更可能影響 ditto 指令行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R08] 自訂 Error 型別未使用 thiserror，違反專案規範</summary>

此 PR 將原本使用 `#[derive(Debug, thiserror::Error)]` 的 Error 列舉改為手動實作 `Display` 和 `Error` trait。這違反了專案規範 R08（所有自訂錯誤型別應使用 thiserror）。手動實作容易出錯且不一致，例如 `source()` 方法中未包含 `Plist`、`Notarize`、`ParseNotarytoolOutput`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER` 等變體，可能導致錯誤鏈不完整。建議改回使用 `thiserror` 並保留原有的 `#[error(...)]` 屬性。

**判斷依據**：diff 中移除了 `#[derive(Debug, thiserror::Error)]` 以及所有 `#[error(...)]` 屬性，改為手動實作 `Display` 和 `Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開 Error 列舉未標記 #[non_exhaustive]</summary>

此 Error 列舉是公開 API，且未來可能新增變體。根據專案規範 R09，公開錯誤列舉應標記 `#[non_exhaustive]` 以避免新增變體時造成破壞性變更。目前此列舉未加上該屬性，建議加上 `#[non_exhaustive]`。

**判斷依據**：diff 中新增的 Error 列舉定義沒有 `#[non_exhaustive]` 屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件邏輯變更可能導致行為錯誤</summary>

原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。此變更會影響何時列印 "Notarizing" 訊息。需要確認此變更是否為預期行為：當 `wait` 為 true 且 status 為 None 時，原本會列印，現在不會；當 `wait` 為 false 且 status 為 None 時，原本不會列印，現在會。請確認此邏輯修正是否正確，並補充測試。

**判斷依據**：diff 中此行由 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> 引數順序變更可能影響 ditto 指令行為</summary>

在 `notarize_inner` 中，`app_bundle_path` 和 `zip_path` 的順序被調換。原本 `app_bundle_path` 在前，現在 `zip_path` 在前。這會影響傳遞給 `ditto` 的引數順序，可能導致壓縮來源和目標錯誤。請確認此變更是否為預期，並驗證產生的 zip 內容是否正確。

**判斷依據**：diff 中顯示兩行順序對調。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12615 (cache hit 10624) ｜ completion tokens 1704 ｜ PR #13</sub>