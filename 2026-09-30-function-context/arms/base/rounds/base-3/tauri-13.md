<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的版本更新，主要將多個 crate 從 2.9.0/2.5.0/2.7.0/2.2.0 升級至 2.9.1/2.5.1/2.7.1/2.3.0，並包含 tauri-macos-sign 的錯誤處理重構（從 thiserror 改為手動實作 Display/Error）以及 notarize_inner 中的一個邏輯修正。整體風險中等，需特別注意 tauri-macos-sign 的錯誤處理變更是否影響下游依賴，以及 notarize_inner 的邏輯修正是否正確。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 中 wait 邏輯可能反轉 | 0.80 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:20` | Error 型別移除 thiserror 衍生可能破壞下游 API | 0.75 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:176` | notarize_inner 中參數順序變更可能影響可讀性 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 中 wait 邏輯可能反轉</summary>

在 `notarize_inner` 中，原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 被改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。這會改變當 `status` 為 `None` 時的行為：原本是 `!wait`（即不等待時才進入），現在變成 `wait`（等待時才進入）。這可能導致在 `wait=false` 且 `status=None` 時，原本會執行的 notarization 流程被跳過，或反之。需要確認此變更是否為預期修正，並檢查相關測試。

**判斷依據**：diff 中此行由 `if submit_output.status.map_or(!wait, |s| s == "Accepted") {` 改為 `if submit_output.status.map_or(wait, |s| s == "Accepted") {`，邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:20</code> Error 型別移除 thiserror 衍生可能破壞下游 API</summary>

原本 `Error` 使用 `thiserror::Error` 衍生，現在改為手動實作 `Display` 和 `std::error::Error`。這可能影響下游依賴此 crate 的程式碼，例如使用 `thiserror` 的 `#[from]` 或依賴 `Error` 的特定 trait 實作。此外，手動實作的 `source()` 方法未包含所有變體（如 `Plist`、`X509Certificate` 等），可能導致錯誤鏈不完整。建議確認此變更是否為有意為之，並考慮提供向後相容的實作。

**判斷依據**：diff 中移除了 `#[derive(Debug, thiserror::Error)]` 改為 `#[derive(Debug)]`，並新增手動實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:176</code> notarize_inner 中參數順序變更可能影響可讀性</summary>

在 `notarize_inner` 中，`app_bundle_path` 和 `zip_path` 的參數順序被調換，這可能只是為了可讀性，但需確認是否影響任何依賴此函數的程式碼（雖然此函數為私有，但可能被測試或內部呼叫）。

**判斷依據**：diff 中參數順序由 `app_bundle_path` 在前改為 `zip_path` 在前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10605 (cache hit 10496) ｜ completion tokens 1002 ｜ PR #13</sub>