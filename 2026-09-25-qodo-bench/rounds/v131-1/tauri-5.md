<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本使用全域靜態變數的 app paths 與 config 改為以參數傳遞，並將 ConfigHandle 從 Mutex 包裝改為直接傳遞 ConfigMetadata。整體方向合理，可減少全域狀態並提升可測試性。但變更範圍極大，涉及多個子命令與平台，需特別注意併發與所有權問題。最關鍵的風險在於 `run_dev_watcher` 中對 `config` 的 Mutex 鎖定可能造成死鎖，以及 `resolve_dirs` 回傳的 `&'static Path` 生命週期可能導致懸垂指標。建議先修正這兩個問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-cli/src/interface/rust.rs:595` | Mutex 鎖定可能造成死鎖 | 0.90 |
| 🛑 | Blocker | `crates/tauri-cli/src/helpers/app_paths.rs:26` | 回傳 &'static Path 可能造成懸垂指標 | 0.85 |
| ⚠️ | Major | `crates/tauri-cli/src/helpers/config.rs:247` | reload_config 可能導致資料競爭 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/ios/mod.rs:272` | features 欄位從 None 改為 Some(empty) 可能改變行為 | 0.75 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/config.rs:74` | 環境變數讀取從 var 改為 var_os 可能影響非 UTF-8 值 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> Mutex 鎖定可能造成死鎖</summary>

在 `run_dev_watcher` 中，`reload_config` 被呼叫時傳入 `&mut config.lock().unwrap()`，但 `reload_config` 內部會再次鎖定同一個 Mutex（透過 `config.lock().unwrap()`），造成死鎖。

具體情境：當監視到設定檔變更時，程式會進入此分支，然後卡死。

建議：先取得鎖定並在鎖定範圍外呼叫 `reload_config`，或修改 `reload_config` 使其接受已鎖定的 guard。

**判斷依據**：diff 中新增的 `reload_config(&mut config.lock().unwrap(), ...)` 呼叫，而 `reload_config` 函式內部會再次呼叫 `config.lock().unwrap()`（見 config.rs 的 `reload_config` 實作）。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:26</code> 回傳 &'static Path 可能造成懸垂指標</summary>

`Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但實際上是從 `OnceLock<PathBuf>` 中取得的參考。雖然 `OnceLock` 是靜態的，但 `PathBuf` 的內容可能在未來被修改或釋放，導致懸垂指標。

具體情境：如果 `OnceLock` 中的值被重新設定（例如在測試中），舊的參考將失效。

建議：改為擁有所有權的 `PathBuf`，或使用 `Arc<Path>` 等安全共享型別。

**判斷依據**：diff 中新增的 `Dirs` 結構體定義，其欄位型別為 `&'static Path`，但來源是 `OnceLock<PathBuf>` 的參考。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/config.rs:247</code> reload_config 可能導致資料競爭</summary>

`reload_config` 接受 `&mut ConfigMetadata`，但呼叫端可能同時有多個執行緒持有同一個 `ConfigMetadata` 的參考（例如在 `run_dev_watcher` 中，`config` 被包在 `Mutex` 中，但鎖定後傳遞的是 `&mut` 參考，而其他執行緒可能也在存取）。

具體情境：在 dev 模式下，檔案監視器執行緒與主執行緒可能同時存取 `config`，導致資料競爭。

建議：確保所有對 `ConfigMetadata` 的存取都透過 Mutex 保護，或使用不可變共享（如 `Arc<RwLock<ConfigMetadata>>`）。

**判斷依據**：diff 中 `reload_config` 的簽名改為接受 `&mut ConfigMetadata`，但呼叫端可能未正確同步。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/ios/mod.rs:272</code> features 欄位從 None 改為 Some(empty) 可能改變行為</summary>

在 `get_config` 中，原本當 `ios_options.features` 為空時，`features` 欄位設為 `None`，現在改為 `Some(ios_options.features)`，即使為空也會是 `Some(vec![])`。這可能影響下游邏輯，例如判斷是否啟用預設 features。

具體情境：如果下游程式碼依賴 `None` 來表示「未指定 features」，則現在會得到 `Some(empty)`，可能導致行為差異。

建議：確認下游對 `features` 的處理，若需要保留原行為，應在空時設為 `None`。

**判斷依據**：diff 中將原本的條件表達式改為直接 `Some(ios_options.features)`，移除了空值檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/config.rs:74</code> 環境變數讀取從 var 改為 var_os 可能影響非 UTF-8 值</summary>

在 `wix_settings` 中，原本使用 `std::env::var` 讀取 `TAURI_BUNDLER_WIX_FIPS_COMPLIANT`，現在改為 `var_os`。`var_os` 回傳 `OsString`，若環境變數包含非 UTF-8 字元，比較 `v == "true"` 可能失敗。

具體情境：若使用者設定該環境變數為非 UTF-8 值，原本會回傳錯誤，現在可能靜默忽略。

建議：確認此變更是否必要，或使用 `to_str()` 進行安全轉換。

**判斷依據**：diff 中將 `std::env::var` 改為 `std::env::var_os`，並直接與字串比較。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36283 (cache hit 1408) ｜ completion tokens 1698 ｜ PR #5</sub>