<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的版本更新，主要將多個 crate 從 2.9.0 升級至 2.9.1（tauri-macos-sign 升級至 2.3.0），並包含 tauri-macos-sign 的錯誤處理重構（從 thiserror 改為手動實作 Display/Error）。整體風險低，但需注意 tauri-macos-sign 的變更可能違反專案規範 R08（應使用 thiserror）與 R09（公開錯誤枚舉應標記 non_exhaustive），且 notarize_inner 中的條件判斷變更需確認邏輯正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R08] 錯誤類型未使用 thiserror，違反專案規範 | 0.90 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開錯誤枚舉未標記 #[non_exhaustive] | 0.85 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件判斷邏輯可能反轉 | 0.80 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | 參數順序變更可能影響命令列行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R08] 錯誤類型未使用 thiserror，違反專案規範</summary>

此變更將原本使用 `#[derive(Debug, thiserror::Error)]` 的 `Error` 枚舉改為手動實作 `Display` 與 `Error` trait。專案規範 R08 要求所有自訂錯誤類型必須使用 thiserror 以維持一致性與可維護性。手動實作容易出錯（例如 `source()` 方法可能遺漏某些變體），且增加維護負擔。建議改回使用 thiserror，並保留原有的 `#[error(...)]` 屬性。

**判斷依據**：diff 中移除了 `#[derive(Debug, thiserror::Error)]`，並新增了手動的 `impl std::fmt::Display for Error` 與 `impl std::error::Error for Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開錯誤枚舉未標記 #[non_exhaustive]</summary>

`Error` 是公開 API 的一部分，且此 PR 的變更說明中標註為「Potentially breaking change」。根據專案規範 R09，公開錯誤枚舉應標記 `#[non_exhaustive]` 以允許未來新增變體而不造成破壞性變更。目前此枚舉未加上該屬性，未來新增錯誤變體將導致下游編譯失敗。建議在 `pub enum Error` 上方加上 `#[non_exhaustive]`。

**判斷依據**：diff 中 `Error` 枚舉為公開且未標記 `#[non_exhaustive]`，且變更日誌中明確指出此為潛在破壞性變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件判斷邏輯可能反轉</summary>

原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。此變更將 `map_or` 的預設值從 `!wait` 改為 `wait`，可能改變行為：當 `status` 為 `None` 時，原本在 `wait == false` 時會進入分支，現在則在 `wait == true` 時進入。需確認此變更是否為預期修正，否則可能導致非等待模式下跳過必要的處理。

**判斷依據**：diff 中明確顯示此行由 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> 參數順序變更可能影響命令列行為</summary>

在 `notarize_inner` 中，`app_bundle_path` 與 `zip_path` 的參數順序被調換。雖然這可能只是為了修正命令列參數的順序，但需確認此變更不會影響實際的 notarization 流程。建議驗證相關測試或手動測試以確保正確性。

**判斷依據**：diff 中顯示 `app_bundle_path` 與 `zip_path` 的順序被交換。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12677 (cache hit 12672) ｜ completion tokens 1178 ｜ PR #13</sub>