<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本使用全域靜態變數的 app paths 與 config 改為以參數傳遞，並調整相關函式簽名。主要風險在於 `Dirs` 結構體持有 `&'static Path`，但 `resolve_dirs` 使用 `OnceLock` 儲存 `PathBuf`，可能導致生命週期問題。此外，部分函式簽名變更後，呼叫端可能未同步更新，造成編譯錯誤。建議優先確認生命週期與所有呼叫點的正確性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/helpers/app_paths.rs:26` | Dirs 結構體持有 &'static Path 可能導致生命週期問題 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/helpers/config.rs:247` | reload_config 函式可能未正確更新所有使用 config 的地方 | 0.70 |
| ⚠️ | Major | `crates/tauri-cli/src/interface/rust.rs:595` | run_dev_watcher 中 reload_config 的錯誤處理可能導致 panic | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/ios/mod.rs:272` | get_config 中 features 欄位改為 Some(ios_options.features) 可能改變行為 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/mod.rs:476` | get_app 中 tauri_dir 參數可能造成不必要的複製 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:26</code> Dirs 結構體持有 &'static Path 可能導致生命週期問題</summary>

`Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但 `resolve_dirs` 函式是從 `OnceLock<PathBuf>` 取得參考。`OnceLock` 的 `get_or_init` 回傳的參考生命週期是 `'static`，因此型別上可行，但若未來實作變更（例如改為每次呼叫都建立新的 `PathBuf`），此設計會造成生命週期錯誤。建議改為持有 `PathBuf` 或使用 `Cow<'static, Path>` 以增加彈性。

**判斷依據**：diff 中新增的 `Dirs` 結構體定義，以及 `resolve_dirs` 函式使用 `OnceLock` 的實作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/config.rs:247</code> reload_config 函式可能未正確更新所有使用 config 的地方</summary>

`reload_config` 現在接受 `&mut ConfigMetadata` 並直接修改其內容，但呼叫端可能仍持有舊的參考或複製，導致不一致。例如在 `dev.rs` 中，`setup` 函式接收 `&mut ConfigMetadata`，但之後又將其包裝成 `Mutex`，若其他執行緒仍使用舊的參考，可能造成資料競爭。建議確認所有呼叫點都正確處理可變參考，並考慮使用 `Arc<RwLock<ConfigMetadata>>` 來共享。

**判斷依據**：diff 中 `reload_config` 的實作，以及 `dev.rs` 中 `setup` 函式接收 `&mut ConfigMetadata` 後又建立 `Mutex` 的程式碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> run_dev_watcher 中 reload_config 的錯誤處理可能導致 panic</summary>

在 `run_dev_watcher` 中，`reload_config(&mut config.lock().unwrap(), merge_configs, dirs.tauri).is_ok()` 若回傳 `Err`，則會忽略錯誤並繼續執行，但後續 `rewrite_manifest(&config.lock().unwrap(), dirs.tauri)?` 可能因為 config 未更新而產生不一致。此外，`config.lock().unwrap()` 若發生 poison 會 panic。建議使用 `if let Ok(mut guard) = config.lock() { ... }` 並妥善處理錯誤。

**判斷依據**：diff 中 `run_dev_watcher` 的片段，顯示 `reload_config` 的錯誤被忽略，且使用 `unwrap` 可能 panic。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/ios/mod.rs:272</code> get_config 中 features 欄位改為 Some(ios_options.features) 可能改變行為</summary>

原本當 `ios_options.features` 為空時，`features` 欄位設為 `None`，現在改為 `Some(ios_options.features)`，即使為空也會是 `Some(vec![])`。這可能影響下游邏輯，例如判斷是否有 features 時，`Some(empty)` 與 `None` 的語意不同。建議確認此變更是否為預期，或保留原本的條件判斷。

**判斷依據**：diff 中 `get_config` 函式內 `features` 欄位的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/mod.rs:476</code> get_app 中 tauri_dir 參數可能造成不必要的複製</summary>

`get_app` 函式新增 `tauri_dir: &Path` 參數，但在函式內先 `let tauri_dir = tauri_dir.to_path_buf();` 再於閉包中使用 `tauri_dir.to_path_buf()`，造成兩次複製。建議直接使用 `tauri_dir.to_path_buf()` 一次，或將閉包改為捕獲 `PathBuf` 的參考。

**判斷依據**：diff 中 `get_app` 函式的實作。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 38438 (cache hit 38400) ｜ completion tokens 1561 ｜ PR #5</sub>