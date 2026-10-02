<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本全域靜態的 app paths 與 config 改為以參數傳遞的 `Dirs` 與 `ConfigMetadata`，大幅降低全域狀態。整體方向正確，但引入了一些潛在問題：`Dirs` 持有 `&'static Path` 卻由 `OnceLock` 初始化，可能造成生命週期與記憶體洩漏疑慮；`resolve_dirs` 在找不到 Tauri 專案時會 panic，與先前行為一致但需確認呼叫端是否已處理；`get_app` 中 `tauri_dir` 參數被遮蔽，可能造成混淆；`reload_config` 在 watcher 中直接 unwrap mutex，若鎖已中毒會 panic；`merge_config_with` 未處理 `serde_json::to_string` 的錯誤；`get_config` 在 iOS 中新增 `tauri_dir` 參數但未使用，可能為疏漏。建議優先修正 mutex 處理與錯誤處理，並確認 `Dirs` 的生命週期設計。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/helpers/app_paths.rs:26` | `Dirs` 持有 `&'static Path` 可能導致生命週期問題 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/interface/rust.rs:595` | `reload_config` 在 watcher 中直接 unwrap mutex，可能 panic | 0.75 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/config.rs:271` | `merge_config_with` 未處理 `serde_json::to_string` 的錯誤 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/mod.rs:476` | `get_app` 中參數 `tauri_dir` 被遮蔽 | 0.65 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/ios/mod.rs:129` | `get_config` 新增的 `tauri_dir` 參數未使用 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:26</code> `Dirs` 持有 `&'static Path` 可能導致生命週期問題</summary>

`Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但其實際指向的 `PathBuf` 儲存在 `OnceLock` 中。雖然 `OnceLock` 的內容在程式結束前不會被釋放，因此生命週期上可行，但這會造成記憶體永遠無法回收，且若未來改為非靜態儲存，將導致 dangling reference。建議改為持有 `PathBuf` 或使用 `Arc<Path>`，以避免潛在的生命週期問題。

**判斷依據**：diff 中新增的 `Dirs` 結構體使用 `&'static Path`，而 `resolve_dirs` 透過 `OnceLock::get_or_init` 初始化 `PathBuf` 並回傳參考。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> `reload_config` 在 watcher 中直接 unwrap mutex，可能 panic</summary>

在 `run_dev_watcher` 中，呼叫 `reload_config(&mut config.lock().unwrap(), ...)`。如果其他執行緒在持有鎖時 panic，Mutex 會進入 poisoned 狀態，此時 `unwrap()` 會導致 panic，進而使 watcher 執行緒崩潰。建議使用 `lock().map_err(...)` 或 `if let Ok(mut guard) = config.lock()` 來處理中毒情況。

**判斷依據**：diff 中此處將原本的 `reload_config(merge_configs)` 改為直接對 `config.lock().unwrap()` 進行可變借用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/config.rs:271</code> `merge_config_with` 未處理 `serde_json::to_string` 的錯誤</summary>

在 `merge_config_with` 中，`serde_json::to_string(&merge_config).unwrap()` 直接 unwrap。雖然 `merge_config` 是由 JSON Value 組成，序列化失敗的可能性極低，但為了穩健性，建議改為 `?` 或 `context` 處理。

**判斷依據**：diff 中此行程式碼在重構後仍保留 unwrap。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/mod.rs:476</code> `get_app` 中參數 `tauri_dir` 被遮蔽</summary>

在 `get_app` 函式中，參數 `tauri_dir: &Path` 被用於建立 `App::from_raw`，但隨後又用 `let tauri_dir = tauri_dir.to_path_buf();` 遮蔽了參數。這可能造成閱讀混淆，建議重新命名變數，例如 `tauri_dir_buf`。

**判斷依據**：diff 中此處新增了遮蔽變數的程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/ios/mod.rs:129</code> `get_config` 新增的 `tauri_dir` 參數未使用</summary>

在 `mobile/ios/mod.rs` 的 `get_config` 函式中，新增了 `tauri_dir: &Path` 參數，但函式體內並未使用。這可能是為了保持介面一致，但若無實際用途，建議移除或加上 `_` 前綴以避免編譯器警告。

**判斷依據**：diff 中此函式簽名新增了 `tauri_dir` 參數，但函式內未使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36319 (cache hit 1536) ｜ completion tokens 1494 ｜ PR #5</sub>