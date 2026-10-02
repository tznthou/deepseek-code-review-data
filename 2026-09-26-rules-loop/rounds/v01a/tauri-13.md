<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要將多個 crate 從 2.9.0/2.5.0/2.7.0/2.2.0 升級至 2.9.1/2.5.1/2.7.1/2.3.0，並包含 tauri-macos-sign 的錯誤處理重構（從 thiserror 改為手動實作 Display/Error）。整體風險低，但需注意 tauri-macos-sign 的變更可能違反專案規範 R08（應使用 thiserror）與 R09（公開錯誤枚舉應標記 non_exhaustive），且 notarize_inner 中的條件判斷變更可能影響行為。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R08] 錯誤類型未使用 thiserror，違反專案規範 | 0.90 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開錯誤枚舉缺少 #[non_exhaustive] | 0.85 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件判斷邏輯可能反轉 | 0.80 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | 參數順序變更可能影響可讀性 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R08] 錯誤類型未使用 thiserror，違反專案規範</summary>

此 PR 將原本使用 `#[derive(Debug, thiserror::Error)]` 的 `Error` 枚舉改為手動實作 `Display` 和 `Error` trait。根據專案規範 R08，所有自訂錯誤類型應使用 thiserror 以維持一致的錯誤處理。手動實作容易出錯且增加維護成本。建議改回使用 thiserror derive，並保留原有的 `#[error(...)]` 屬性。

**判斷依據**：diff 中顯示 `-#[derive(Debug, thiserror::Error)]` 被移除，改為 `+#[derive(Debug)]`，並新增手動的 `impl std::fmt::Display for Error` 和 `impl std::error::Error for Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開錯誤枚舉缺少 #[non_exhaustive]</summary>

`Error` 是公開的錯誤枚舉，但未標記 `#[non_exhaustive]`。根據專案規範 R09，公開錯誤枚舉應標記為 non_exhaustive，以便未來新增變體而不造成破壞性變更。建議在 `pub enum Error` 上方加上 `#[non_exhaustive]`。

**判斷依據**：diff 中 `Error` 枚舉為公開且未見 `#[non_exhaustive]` 屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件判斷邏輯可能反轉</summary>

原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。這會改變當 `status` 為 `None` 時的行為：原本在 `wait` 為 false 時會進入 if 區塊，現在則是在 `wait` 為 true 時才會進入。這可能導致在非等待模式下跳過必要的處理，或在等待模式下執行不該執行的程式碼。請確認此變更是否為預期行為，並補充測試。

**判斷依據**：diff 中顯示 `-    if submit_output.status.map_or(!wait, |s| s == "Accepted") {` 改為 `+    if submit_output.status.map_or(wait, |s| s == "Accepted") {`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> 參數順序變更可能影響可讀性</summary>

在 `notarize_inner` 中，`app_bundle_path` 和 `zip_path` 的參數順序被調換。雖然功能上可能無影響，但這可能導致呼叫端混淆，建議確認所有呼叫點都已同步更新，並考慮是否為必要變更。

**判斷依據**：diff 中顯示原本 `app_bundle_path` 在前，`zip_path` 在後，現在順序對調。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12687 (cache hit 10496) ｜ completion tokens 1166 ｜ PR #13</sub>