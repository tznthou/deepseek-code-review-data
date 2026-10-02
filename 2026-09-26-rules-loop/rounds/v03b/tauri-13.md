<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的多個 crate 進行版本更新（patch/minor），主要包含：移除 .changes 檔案、更新 Cargo.toml 與 Cargo.lock 的相依版本、更新 CHANGELOG、以及修改 tauri-macos-sign 的錯誤型別（從 thiserror 改為手動實作 Display/Error）。整體風險中等，主要問題在於 tauri-macos-sign 的錯誤型別變更可能違反專案規範（R08、R09），且未新增對應的變更檔案（R13）。此外，notarize_inner 中的條件判斷變更可能引入邏輯錯誤，需進一步確認。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:20` | [R08] 錯誤型別未使用 thiserror，違反專案規範 | 0.90 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開錯誤列舉未標記 #[non_exhaustive] | 0.85 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件判斷邏輯可能反轉 | 0.80 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:20` | 錯誤型別變更未新增變更檔案 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:20</code> [R08] 錯誤型別未使用 thiserror，違反專案規範</summary>

此變更將原本使用 `#[derive(Debug, thiserror::Error)]` 的 `Error` 列舉改為手動實作 `Display` 和 `Error` trait。專案規範 R08 明確要求所有自訂錯誤型別必須使用 thiserror 來提供一致的錯誤處理。手動實作可能導致錯誤訊息不一致、增加維護成本，且容易遺漏 `source` 方法的正確實作。建議保留 thiserror 的 derive，或提供充分理由說明為何需要手動實作。

**判斷依據**：diff 中移除了 `#[derive(Debug, thiserror::Error)]` 並改為 `#[derive(Debug)]`，且新增了手動的 `Display` 和 `Error` 實作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開錯誤列舉未標記 #[non_exhaustive]</summary>

此 `Error` 列舉為公開 API，且未來可能新增變體。專案規範 R09 要求公開錯誤列舉應標記 `#[non_exhaustive]` 以避免新增變體時造成破壞性變更。目前變更未加上此屬性，可能導致下游使用者在未來版本更新時遇到編譯錯誤。建議加上 `#[non_exhaustive]`。

**判斷依據**：diff 中 `pub enum Error {` 沒有 `#[non_exhaustive]` 屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件判斷邏輯可能反轉</summary>

原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。這可能改變了行為：當 `status` 為 `None` 時，原本在 `wait` 為 false 時會進入分支，現在則在 `wait` 為 true 時進入。需要確認此變更是否為預期的修正，否則可能導致在等待模式下跳過必要的處理。

**判斷依據**：diff 中該行從 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:20</code> 錯誤型別變更未新增變更檔案</summary>

此 PR 包含對 `tauri-macos-sign` 的錯誤型別變更，這是一個公開 API 的變更，可能影響下游使用者。根據專案規範 R13，所有需要版本提升的變更都應包含對應的變更檔案（.changes 目錄）。目前 diff 中刪除了 `.changes/macos-codesign-error-enum.md`，但未新增新的變更檔案，可能導致版本管理不一致。

**判斷依據**：diff 顯示刪除了 `.changes/macos-codesign-error-enum.md`，但沒有新增對應的變更檔案。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12697 (cache hit 12672) ｜ completion tokens 1130 ｜ PR #13</sub>