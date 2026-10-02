<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本全域靜態的 app paths 與 config 改為以參數傳遞的 `Dirs` 與 `ConfigMetadata`，大幅減少全域狀態。整體方向合理，但涉及大量函式簽名變更，需注意併發與生命週期問題。最關鍵的風險在於 `resolve_dirs()` 回傳的 `&'static Path` 可能指向無效記憶體，以及 `dev` 流程中 `Mutex<ConfigMetadata>` 的鎖定可能導致死鎖或資料競爭。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-cli/src/helpers/app_paths.rs:26` | `resolve_dirs()` 回傳的 `&'static Path` 可能指向無效記憶體 | 0.95 |
| ⚠️ | Major | `crates/tauri-cli/src/interface/rust.rs:595` | `run_dev_watcher` 中鎖定 `Mutex<ConfigMetadata>` 可能導致死鎖或長時間阻塞 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/helpers/config.rs:247` | `reload_config` 可能導致資料競爭或遺失更新 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/build.rs:122` | `tauri_config` 被包裝在 `Mutex` 中，但後續使用時可能過早釋放鎖 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/ios/build.rs:170` | `command` 函式新增 `dirs` 參數，但未在所有呼叫點傳遞 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:26</code> `resolve_dirs()` 回傳的 `&'static Path` 可能指向無效記憶體</summary>

`Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但其實際指向的是 `OnceLock<PathBuf>` 中的資料。`OnceLock` 的 `get_or_init` 方法回傳 `&T`，其生命週期與 `OnceLock` 本身相同，而 `OnceLock` 是靜態變數，因此生命週期確實是 `'static`。然而，如果 `resolve_dirs()` 被呼叫多次，且第二次呼叫時 `OnceLock` 已經初始化，則回傳的參考仍然有效。但若 `OnceLock` 尚未初始化，則 `get_or_init` 會初始化並回傳參考，此參考在 `OnceLock` 的生命週期內有效。因此，此處的 `&'static Path` 實際上是安全的，但前提是 `OnceLock` 永遠不會被重新初始化或釋放。在目前的程式碼中，`OnceLock` 是靜態的，因此不會被釋放。然而，這種設計使得 `Dirs` 結構體的生命週期與靜態變數綁定，可能導致未來難以重構。此外，如果 `resolve_dirs()` 在 `OnceLock` 初始化之前被呼叫，則會觸發初始化，但若初始化失敗（例如找不到 Tauri 目錄），則會 panic。這在原本的 `resolve()` 函式中也是如此。因此，此處的風險主要在於設計上的脆弱性，而非立即的記憶體安全問題。

**判斷依據**：diff 中新增的 `Dirs` 結構體使用 `&'static Path`，但實際資料儲存在 `OnceLock<PathBuf>` 中。雖然 `OnceLock` 是靜態的，但這種設計使得 `Dirs` 的生命週期與靜態變數綁定，可能導致未來難以重構。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> `run_dev_watcher` 中鎖定 `Mutex<ConfigMetadata>` 可能導致死鎖或長時間阻塞</summary>

在 `run_dev_watcher` 中，程式碼使用 `config.lock().unwrap()` 取得 `ConfigMetadata` 的鎖，然後呼叫 `reload_config` 和 `rewrite_manifest`。如果 `reload_config` 或 `rewrite_manifest` 內部再次嘗試鎖定同一個 `Mutex`，則會導致死鎖。此外，如果鎖定被長時間持有，可能會阻塞其他執行緒。建議改用 `try_lock` 或將鎖定範圍最小化。

**判斷依據**：diff 中顯示在 `run_dev_watcher` 中直接呼叫 `config.lock().unwrap()`，且在同一表達式中多次鎖定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/config.rs:247</code> `reload_config` 可能導致資料競爭或遺失更新</summary>

`reload_config` 函式直接將 `*config = load_config(...)` 賦值給傳入的 `&mut ConfigMetadata`。如果有多個執行緒同時持有同一個 `ConfigMetadata` 的可變參考，則會導致資料競爭。雖然目前呼叫點大多在單一執行緒中，但未來若引入多執行緒，此處將成為風險。建議使用 `Mutex` 或 `RwLock` 保護 `ConfigMetadata`。

**判斷依據**：diff 中新增的 `reload_config` 函式直接賦值給 `&mut ConfigMetadata`，沒有同步機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/build.rs:122</code> `tauri_config` 被包裝在 `Mutex` 中，但後續使用時可能過早釋放鎖</summary>

在 `command` 函式中，`tauri_config` 被建立為 `Mutex::new(get_tauri_config(...)?)`，然後傳遞給 `run` 函式。在 `run` 函式中，程式碼使用 `let tauri_config = &tauri_config.lock().unwrap();` 取得鎖，但此鎖在 `run` 函式結束前可能被釋放，而後續程式碼仍使用 `tauri_config` 參考。這可能導致生命週期問題。建議將鎖的持有範圍明確化，或直接傳遞 `ConfigMetadata` 而非 `Mutex`。

**判斷依據**：diff 中顯示 `tauri_config` 被包裝在 `Mutex` 中，並在 `run` 函式中使用 `lock().unwrap()` 取得參考。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/ios/build.rs:170</code> `command` 函式新增 `dirs` 參數，但未在所有呼叫點傳遞</summary>

`ios::build::command` 的簽名從 `(options, noise_level)` 改為 `(options, noise_level, dirs: &Dirs)`，但可能有些呼叫點未更新，導致編譯錯誤。請確認所有呼叫點都已傳入 `dirs`。

**判斷依據**：diff 中顯示 `command` 函式新增了 `dirs` 參數，但未顯示所有呼叫點。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36283 (cache hit 36224) ｜ completion tokens 1903 ｜ PR #5</sub>