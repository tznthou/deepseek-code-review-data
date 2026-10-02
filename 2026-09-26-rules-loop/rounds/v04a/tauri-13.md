<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的版本更新，主要將多個 crate 從 2.9.0 升級至 2.9.1（tauri-macos-sign 為 2.3.0），並包含相依性更新與 changelog 調整。核心程式碼變更在 tauri-macos-sign/src/lib.rs：移除 thiserror 衍生、改為手動實作 Display 與 Error trait，並修正 notarize_inner 中的引數順序與條件邏輯。整體風險中等，需特別注意 Error 型別的 API 相容性與 notarize_inner 的邏輯變更是否正確。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開 Error enum 未標記 #[non_exhaustive] | 0.90 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件邏輯變更可能導致行為錯誤 | 0.85 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | 引數順序變更可能影響 ditto 命令行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開 Error enum 未標記 #[non_exhaustive]</summary>

此 Error enum 為公開 API，且此 PR 將其從 thiserror 衍生改為手動實作，但未加上 #[non_exhaustive]。這會讓下游使用者在 match 此 enum 時，未來新增 variant 會造成 breaking change。建議加上 #[non_exhaustive] 屬性。

**判斷依據**：diff 中顯示 `pub enum Error {`，且無 `#[non_exhaustive]` 屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件邏輯變更可能導致行為錯誤</summary>

原本 `if submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `if submit_output.status.map_or(wait, |s| s == "Accepted")`。此變更反轉了當 status 為 None 時的行為：原本在 wait=false 時會進入 if，現在變成 wait=true 時才會進入。需確認此變更是否符合預期，否則可能導致在非等待模式下跳過必要的處理。

**判斷依據**：diff 中此行由 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> 引數順序變更可能影響 ditto 命令行為</summary>

在 notarize_inner 中，`app_bundle_path` 與 `zip_path` 的順序被調換。若 ditto 命令對引數順序敏感，可能導致壓縮內容錯誤。需確認此變更是否為修正或意外。

**判斷依據**：diff 顯示原本 app_bundle_path 在前，現在 zip_path 在前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11660 (cache hit 10496) ｜ completion tokens 812 ｜ PR #13</sub>