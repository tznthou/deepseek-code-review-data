<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本以全域靜態變數儲存的 Tauri 目錄、前端目錄與設定，改為透過 `Dirs` 結構與函式參數傳遞，以減少內部靜態狀態。整體方向合理，但改動範圍極大，涉及多個子命令與平台建置流程。主要風險在於 `resolve_dirs()` 使用 `OnceLock` 快取路徑，若測試或程式在單一程序中多次呼叫且環境變數改變，可能取得舊值；此外，部分函式簽名變更後，呼叫端傳入的 `tauri_dir` 參數與內部重新計算的 `tauri_dir` 可能不一致，需確認所有路徑解析邏輯一致。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/helpers/app_paths.rs:130` | `resolve_dirs()` 使用 `OnceLock` 快取路徑，可能導致測試或動態環境變更時取得舊值 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/helpers/config.rs:152` | `load_config` 中 `tauri_dir` 參數可能與內部重新計算的 `tauri_dir` 不一致 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/interface/rust.rs:595` | `run_dev_watcher` 中 `reload_config` 可能造成死鎖或資料競爭 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/ios/mod.rs:272` | `get_config` 中 `features` 欄位從條件設定改為一律 `Some`，可能改變行為 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/ios/xcode_script.rs:89` | `xcode_script` 中重複呼叫 `read_options` 可能導致不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:130</code> `resolve_dirs()` 使用 `OnceLock` 快取路徑，可能導致測試或動態環境變更時取得舊值</summary>

`resolve_dirs()` 使用 `OnceLock` 的 `get_or_init` 來初始化 `TAURI_DIR` 和 `FRONTEND_DIR`。這表示在一個程序的生命週期內，第一次呼叫後，後續呼叫都會回傳相同的路徑，即使環境變數（如 `TAURI_APP_PATH`、`TAURI_FRONTEND_PATH`）或目前工作目錄已經改變。

**失敗情境**：在測試中，若先以某個工作目錄呼叫 `resolve_dirs()`，之後 `std::env::set_current_dir` 切換到另一個 Tauri 專案，再呼叫 `resolve_dirs()`，仍會回傳第一個專案的路徑，導致後續操作作用在錯誤的目錄上。

**建議**：若需要支援動態變更，應考慮每次重新解析，或提供明確的 reset 機制。若確定程式只會解析一次，則應在文件或註解中說明此限制。

**判斷依據**：diff 中新增的 `resolve_dirs` 函式使用 `TAURI_DIR.get_or_init` 與 `FRONTEND_DIR.get_or_init`，而 `TAURI_DIR` 與 `FRONTEND_DIR` 是 `OnceLock<PathBuf>` 靜態變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/config.rs:152</code> `load_config` 中 `tauri_dir` 參數可能與內部重新計算的 `tauri_dir` 不一致</summary>

`load_config` 接收 `tauri_dir: &Path` 參數，但在函式內部仍呼叫 `super::app_paths::tauri_dir()`（已移除）或使用傳入的 `tauri_dir`？從 diff 來看，原本的 `get_internal` 使用 `super::app_paths::tauri_dir()`，現在改為使用傳入的 `tauri_dir`。然而，在 `reload_config` 中，呼叫 `load_config` 時傳入的是 `tauri_dir` 參數，但 `reload_config` 的 `tauri_dir` 參數來自呼叫端，可能與最初載入設定時使用的 `tauri_dir` 不同。

**失敗情境**：若程式在載入設定後改變了目前工作目錄，或呼叫 `reload_config` 時傳入了不同的 `tauri_dir`，則重新載入的設定可能來自錯誤的目錄，導致設定不一致。

**建議**：確保所有呼叫 `load_config` 的地方都使用相同的 `tauri_dir` 來源，或將 `tauri_dir` 儲存在 `ConfigMetadata` 中，避免不一致。

**判斷依據**：diff 中 `load_config` 新增 `tauri_dir` 參數，但 `reload_config` 函式也接收 `tauri_dir` 參數並傳遞給 `load_config`，呼叫端可能傳入不同的路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> `run_dev_watcher` 中 `reload_config` 可能造成死鎖或資料競爭</summary>

在 `run_dev_watcher` 中，程式碼使用 `reload_config(&mut config.lock().unwrap(), merge_configs, dirs.tauri)`。`config` 是 `&Mutex<ConfigMetadata>`，`config.lock().unwrap()` 會取得 MutexGuard，然後傳遞 `&mut` 給 `reload_config`。如果 `reload_config` 內部再次嘗試鎖定同一個 Mutex（例如透過其他函式），就會造成死鎖。目前 `reload_config` 的實作是直接修改傳入的 `&mut ConfigMetadata`，沒有再鎖定，所以可能安全，但這種模式容易在未來引入錯誤。

**失敗情境**：若未來 `reload_config` 或相關函式需要存取同一個 `Mutex`，就會發生死鎖。

**建議**：避免在持有 MutexGuard 的情況下呼叫可能再鎖定的函式，或改用其他同步機制。

**判斷依據**：diff 中 `run_dev_watcher` 的修改顯示 `reload_config` 被呼叫時傳入了 `&mut config.lock().unwrap()`，而 `config` 是 `&Mutex<ConfigMetadata>`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/ios/mod.rs:272</code> `get_config` 中 `features` 欄位從條件設定改為一律 `Some`，可能改變行為</summary>

在 `get_config` 函式中，原本的程式碼是：
```rust
features: if ios_options.features.is_empty() {
  None
} else {
  Some(ios_options.features)
},
```
現在改為：
```rust
features: Some(ios_options.features),
```
這表示即使 `ios_options.features` 是空的，也會設定為 `Some(vec![])` 而不是 `None`。這可能影響下游對 `features` 欄位的處理，例如某些邏輯可能依賴 `None` 來表示「未指定」。

**失敗情境**：若下游程式碼檢查 `features.is_none()` 來決定是否使用預設值，則現在會得到 `Some(empty)`，可能導致行為差異。

**建議**：確認此變更是否為預期，並檢查所有使用 `features` 欄位的地方是否正確處理空 `Vec`。

**判斷依據**：diff 中 `get_config` 函式的修改顯示 `features` 欄位從條件設定改為直接 `Some(ios_options.features)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/ios/xcode_script.rs:89</code> `xcode_script` 中重複呼叫 `read_options` 可能導致不一致</summary>

在 `xcode_script::command` 中，原本的程式碼先呼叫 `read_options` 取得 `cli_options`，然後在後續的區塊中又呼叫了一次 `read_options`。現在 diff 顯示第一個 `read_options` 的結果被用於判斷是否需要 reload，但第二個 `read_options` 仍然存在，且可能基於 reload 後的 `tauri_config`。這可能導致兩次讀取的選項不一致，尤其是在 reload 之後。

**失敗情境**：若 reload 改變了設定，第二次 `read_options` 可能回傳不同的 `cli_options`，但程式碼可能仍使用第一次的結果，造成邏輯錯誤。

**建議**：只呼叫一次 `read_options`，並在 reload 後重新讀取，或明確區分兩次讀取的目的。

**判斷依據**：diff 中 `xcode_script::command` 的修改顯示 `read_options` 被呼叫兩次，且第二次在 reload 之後。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 38401 (cache hit 36224) ｜ completion tokens 2291 ｜ PR #5</sub>