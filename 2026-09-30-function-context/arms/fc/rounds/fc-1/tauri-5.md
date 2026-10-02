<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本以全域靜態變數儲存的 app paths 與 config 改為以參數傳遞的 `Dirs` 與 `ConfigMetadata`，大幅減少內部靜態狀態。整體方向合理，但涉及大量函式簽名變更，需注意以下風險：
1. `resolve_dirs()` 使用 `OnceLock` 快取路徑，若在不同目錄間切換（例如測試或程式內變更工作目錄）可能回傳舊值。
2. `dev.rs` 中 `setup` 函式將 `ConfigMetadata` 以 `Mutex` 包裝後傳遞給 `interface.dev`，但 `interface.dev` 內部可能同時需要讀取與修改 config，需確認鎖定範圍與生命週期。
3. 部分函式（如 `get_app`）在 closure 中複製 `tauri_dir` 為 `PathBuf`，可能造成不必要的記憶體配置，但影響輕微。
4. 測試程式碼中直接呼叫 `resolve_dirs()` 可能依賴目前工作目錄，需確保測試環境正確。
建議優先確認 `resolve_dirs` 的快取行為是否符合預期，以及 `dev` 流程中 config 的鎖定與傳遞是否正確。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/helpers/app_paths.rs:130` | `resolve_dirs()` 使用 `OnceLock` 快取路徑，可能在不同工作目錄間切換時回傳舊值 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/dev.rs:126` | `setup` 函式將 `ConfigMetadata` 包裝為 `Mutex` 後傳遞給 `interface.dev`，可能造成鎖定衝突 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/mod.rs:476` | `get_app` 在 closure 中複製 `tauri_dir` 為 `PathBuf`，可能造成不必要的記憶體配置 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/interface/rust.rs:1771` | 測試程式碼直接呼叫 `resolve_dirs()`，可能依賴目前工作目錄 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:130</code> `resolve_dirs()` 使用 `OnceLock` 快取路徑，可能在不同工作目錄間切換時回傳舊值</summary>

`resolve_dirs()` 使用 `TAURI_DIR` 和 `FRONTEND_DIR` 兩個 `OnceLock` 來快取解析結果。一旦第一次呼叫後，後續呼叫即使工作目錄改變，仍會回傳相同的路徑。這在 CLI 工具中可能造成問題，例如在同一個程序內處理多個專案（如測試或未來功能）。建議改為每次重新解析，或提供清除快取的機制。

**判斷依據**：diff 中新增的 `resolve_dirs` 函式使用 `OnceLock` 的 `get_or_init`，且 `TAURI_DIR` 和 `FRONTEND_DIR` 為靜態變數，因此只會初始化一次。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/dev.rs:126</code> `setup` 函式將 `ConfigMetadata` 包裝為 `Mutex` 後傳遞給 `interface.dev`，可能造成鎖定衝突</summary>

在 `command_internal` 中，`cfg` 被移動到 `Mutex` 中，然後傳遞給 `interface.dev`。`interface.dev` 內部（如 `run_dev_watcher`）會嘗試鎖定該 `Mutex` 來讀取或修改 config。若呼叫鏈中其他地方也持有鎖，可能導致死鎖或長時間阻塞。建議確認鎖的持有範圍，或改為傳遞 `&Mutex<ConfigMetadata>` 並在必要時才鎖定。

**判斷依據**：diff 中 `command_internal` 建立 `Mutex` 並傳遞給 `interface.dev`，而 `interface.dev` 的實作（在 `interface/rust.rs`）會使用 `config.lock().unwrap()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/mod.rs:476</code> `get_app` 在 closure 中複製 `tauri_dir` 為 `PathBuf`，可能造成不必要的記憶體配置</summary>

`get_app` 函式中，為了在 closure 中使用 `tauri_dir`，先將其轉為 `PathBuf` 並 move 進 closure。這會導致每次呼叫 `get_app` 都複製一份路徑，雖然成本不高，但可以考慮直接傳遞 `&Path` 並在 closure 中使用 `to_path_buf()` 或調整 closure 的生命週期。

**判斷依據**：diff 中 `get_app` 函式新增 `let tauri_dir = tauri_dir.to_path_buf();` 並在 closure 中使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/interface/rust.rs:1771</code> 測試程式碼直接呼叫 `resolve_dirs()`，可能依賴目前工作目錄</summary>

在測試模組中，`parse_target_dir_from_opts` 測試直接呼叫 `crate::helpers::app_paths::resolve_dirs()`。如果測試執行時的工作目錄不是 Tauri 專案，`resolve_dirs` 會 panic。建議在測試中設定明確的環境變數或使用暫存目錄來避免依賴。

**判斷依據**：diff 中測試函式 `parse_target_dir_from_opts` 新增呼叫 `resolve_dirs()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 66708 (cache hit 1536) ｜ completion tokens 1743 ｜ PR #5</sub>