<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本以全域靜態變數儲存的 Tauri 專案路徑（tauri_dir、frontend_dir）與設定（ConfigHandle）改為透過參數傳遞的 Dirs 結構與 ConfigMetadata 值。整體方向合理，可降低全域狀態帶來的耦合與測試困難。主要風險在於大量函式簽名變更可能引入傳遞錯誤的路徑或設定，特別是在行動平台（Android/iOS）與開發監看（watch）流程中。此外，部分程式碼仍使用 Mutex 包裝 ConfigMetadata，但鎖定範圍與生命週期需謹慎檢視，避免死結或資料競爭。建議優先確認所有呼叫點皆傳入正確的 tauri_dir，並檢查 reload_config 與 merge_config_with 的互動是否正確。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/helpers/config.rs:253` | reload_config 可能未正確更新 ConfigMetadata 的 extensions 欄位 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/interface/rust.rs:595` | run_dev_watcher 中鎖定 config 可能造成死結或長時間阻塞 | 0.70 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/build.rs:154` | Android build 中 tauri_config 的 Mutex 可能被過早釋放或重複鎖定 | 0.70 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/ios/build.rs:187` | iOS build 中 tauri_config 的 Mutex 可能被過早釋放或重複鎖定 | 0.70 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/ios/dev.rs:187` | iOS dev 中 tauri_config 的 Mutex 可能被過早釋放或重複鎖定 | 0.70 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/mod.rs:289` | use_network_address_for_dev_url 中 reload_config 可能未正確更新 ConfigMetadata | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/app_paths.rs:140` | resolve_dirs 使用 get_or_init 可能導致 panic 訊息不一致 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/config.rs:274` | merge_config_with 未更新 original_identifier 或 extensions | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/interface/rust.rs:466` | get_watch_folders 中 workspace_path 可能指向錯誤目錄 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/android_studio_script.rs:49` | Android Studio script 中 tauri_config 的 Mutex 可能被重複鎖定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/config.rs:253</code> reload_config 可能未正確更新 ConfigMetadata 的 extensions 欄位</summary>

在 `reload_config` 中，直接以 `*config = load_config(...)` 覆寫整個 ConfigMetadata。但 `load_config` 會重新解析設定檔並建立新的 extensions HashMap，這可能導致先前透過 `merge_config_with` 合併的擴充設定遺失。若呼叫端在 reload 後仍依賴舊的 extensions（例如 `find_bundle_identifier_overwriter`），可能得到不一致的結果。建議確認 reload 後 extensions 是否需要保留或重新合併。

**判斷依據**：diff 中 `reload_config` 函式直接指派 `*config`，而 `load_config` 會建立新的 `extensions` HashMap，未保留先前合併的內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> run_dev_watcher 中鎖定 config 可能造成死結或長時間阻塞</summary>

在 `run_dev_watcher` 中，程式碼執行 `reload_config(&mut config.lock().unwrap(), ...)`，這會在鎖定 Mutex 的同時進行檔案 I/O 與設定解析。若其他執行緒同時嘗試鎖定同一個 Mutex，可能導致阻塞。此外，若 `reload_config` 內部 panic，Mutex 會變成 poisoned，後續操作將失敗。建議縮小鎖定範圍，僅在必要時鎖定，並考慮使用 `try_lock` 或將鎖定移至 reload 之外。

**判斷依據**：diff 中 `run_dev_watcher` 直接呼叫 `config.lock().unwrap()` 並傳遞可變參考給 `reload_config`，鎖定範圍涵蓋整個 reload 過程。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/build.rs:154</code> Android build 中 tauri_config 的 Mutex 可能被過早釋放或重複鎖定</summary>

在 `run` 函式中，先建立 `let tauri_config = &tauri_config.lock().unwrap();` 取得參考，但後續又將 `tauri_config` 傳遞給多個函式，這些函式可能再次嘗試鎖定同一個 Mutex（例如 `crate::build::setup` 內部可能鎖定）。若鎖定非可重入，將導致死結。建議確認所有被呼叫的函式不會再鎖定同一個 Mutex，或改為傳遞 `ConfigMetadata` 的參考而非 Mutex 本身。

**判斷依據**：diff 中 `run` 函式先鎖定取得參考，但後續呼叫 `crate::build::setup(&interface, &mut build_options, tauri_config, true, dirs)` 時傳遞的是 `&ConfigMetadata`，但 `tauri_config` 本身是 `&Mutex<ConfigMetadata>`，此處型別可能不符，需檢查實際程式碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/ios/build.rs:187</code> iOS build 中 tauri_config 的 Mutex 可能被過早釋放或重複鎖定</summary>

類似 Android build，`command` 函式建立 `tauri_config` 後，在 `run_build` 中傳遞 `tauri_config`（型別為 `ConfigMetadata`），但 `run_build` 內部又呼叫 `crate::build::setup`，該函式可能預期 `&ConfigMetadata` 而非 `&Mutex<ConfigMetadata>`。需確認型別一致性，避免編譯錯誤或執行期問題。

**判斷依據**：diff 中 `command` 取得 `tauri_config` 後，傳遞給 `run_build`，但 `run_build` 的參數型別為 `ConfigMetadata`，而 `command` 中的 `tauri_config` 可能是 `Mutex<ConfigMetadata>`，需檢查實際型別。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/ios/dev.rs:187</code> iOS dev 中 tauri_config 的 Mutex 可能被過早釋放或重複鎖定</summary>

在 `run_command` 中，`tauri_config` 為 `ConfigMetadata`，但後續傳遞給 `run_dev` 時，`run_dev` 內部又將其包裝為 `Mutex`。需確認所有路徑的型別一致，且鎖定範圍正確。

**判斷依據**：diff 中 `run_command` 取得 `tauri_config` 後，傳遞給 `run_dev`，但 `run_dev` 的參數型別為 `ConfigMetadata`，而後續在 `run_dev` 中建立 `Mutex::new(tauri_config)`，需確認呼叫端是否已正確傳遞。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/mod.rs:289</code> use_network_address_for_dev_url 中 reload_config 可能未正確更新 ConfigMetadata</summary>

在 `use_network_address_for_dev_url` 中，呼叫 `reload_config(config, ...)` 後，`config` 的內容會被覆寫。但此函式可能被多個執行緒呼叫，且 `config` 是 `&mut ConfigMetadata`，需確保沒有資料競爭。此外，reload 後 `dev_url` 的變更是否會正確反映在後續流程中？建議確認 reload 後 `config.build.dev_url` 是否已更新。

**判斷依據**：diff 中 `use_network_address_for_dev_url` 呼叫 `reload_config`，但未檢查 reload 後 `config.build.dev_url` 是否已更新，可能導致後續使用舊值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:140</code> resolve_dirs 使用 get_or_init 可能導致 panic 訊息不一致</summary>

`resolve_dirs` 中，`TAURI_DIR.get_or_init` 的初始化閉包在找不到 Tauri 專案時會 panic，但 `FRONTEND_DIR.get_or_init` 的閉包則使用 `tauri.parent().unwrap()`，若 `tauri` 為根目錄，`parent()` 可能回傳 None 而 panic。建議提供更明確的錯誤訊息。

**判斷依據**：diff 中 `FRONTEND_DIR.get_or_init` 使用 `tauri.parent().unwrap()`，若 `tauri` 為根目錄，`parent()` 回傳 None，導致 panic。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/config.rs:274</code> merge_config_with 未更新 original_identifier 或 extensions</summary>

`merge_config_with` 僅更新 `config.inner`，但未更新 `original_identifier` 或 `extensions`。若合併的設定包含 identifier 變更，`find_bundle_identifier_overwriter` 可能無法正確識別覆寫來源。建議在合併後重新計算相關欄位。

**判斷依據**：diff 中 `merge_config_with` 僅更新 `config.inner`，未處理 `original_identifier` 與 `extensions`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/interface/rust.rs:466</code> get_watch_folders 中 workspace_path 可能指向錯誤目錄</summary>

`get_watch_folders` 使用 `get_workspace_dir(tauri_dir)` 取得 workspace 根目錄，但若 `tauri_dir` 本身不是 workspace 成員，可能導致監看錯誤的資料夾。建議確認 `get_workspace_dir` 的實作是否能正確處理各種 Cargo workspace 配置。

**判斷依據**：diff 中 `get_watch_folders` 呼叫 `get_workspace_dir(tauri_dir)`，但未驗證 `tauri_dir` 是否為 workspace 成員。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/android_studio_script.rs:49</code> Android Studio script 中 tauri_config 的 Mutex 可能被重複鎖定</summary>

在 `command` 中，`tauri_config` 為 `ConfigMetadata`，但後續傳遞給 `get_config` 時，`get_config` 可能預期 `&ConfigMetadata`，而此處傳遞的是 `&tauri_config`，型別應正確。但需注意 `tauri_config` 是否在其他地方被包裝為 Mutex，導致不一致。

**判斷依據**：diff 中 `command` 取得 `tauri_config` 後，傳遞給 `get_config`，但 `get_config` 的參數型別需確認。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 66708 (cache hit 66688) ｜ completion tokens 3045 ｜ PR #5</sub>