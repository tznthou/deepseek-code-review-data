<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本以全域靜態變數（OnceLock）儲存的 Tauri 目錄與前端目錄，以及全域 Mutex 管理的設定，改為在函式間傳遞的 Dirs 結構與 ConfigMetadata 值。整體方向合理，可降低隱含狀態與測試困難度。主要風險在於併發情境下 Mutex 鎖的取得與釋放時機，以及部分函式簽名變更後，呼叫端是否正確傳遞了 tauri_dir。建議優先確認 dev 流程中 watcher 的鎖定行為，以及 iOS 建置中 features 欄位的變更是否會造成空陣列被序列化。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/interface/rust.rs:595` | 在條件判斷中取得 Mutex 鎖可能導致死鎖或鎖定時間過長 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/ios/mod.rs:272` | iOS 建置設定中 features 欄位從 None 改為 Some(空陣列) 可能改變序列化行為 | 0.75 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/config.rs:253` | reload_config 直接覆寫整個 ConfigMetadata 可能遺失未重新載入的欄位 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/app_paths.rs:131` | resolve_dirs 使用 get_or_init 可能導致 panic 訊息不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> 在條件判斷中取得 Mutex 鎖可能導致死鎖或鎖定時間過長</summary>

在 `run_dev_watcher` 中，`reload_config` 的呼叫被包在 `is_configuration_file(...) && reload_config(&mut config.lock().unwrap(), ...).is_ok()` 的條件中。`config.lock().unwrap()` 取得的 MutexGuard 會一直存活到整個條件式結束，包含 `reload_config` 執行期間。若 `reload_config` 內部或後續的 `rewrite_manifest` 需要再次取得同一個鎖，會造成死鎖。此外，鎖定時間涵蓋了檔案 I/O 與解析，可能阻塞其他執行緒。建議先取得鎖並存入變數，再進行條件判斷與操作，或縮小鎖定範圍。

**判斷依據**：diff 中新增的 `reload_config(&mut config.lock().unwrap(), ...)` 呼叫位於條件式中，MutexGuard 的生命週期延伸至整個條件式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/ios/mod.rs:272</code> iOS 建置設定中 features 欄位從 None 改為 Some(空陣列) 可能改變序列化行為</summary>

原本當 `ios_options.features` 為空時，`features` 欄位設為 `None`；現在改為 `Some(ios_options.features)`，即使為空也會是 `Some(vec![])`。若後續序列化時未特別處理，可能輸出 `features: []` 而非省略該欄位，導致與舊版設定檔或工具不相容。請確認此變更是否會影響產生的 Xcode 專案或設定檔格式。

**判斷依據**：diff 中原本的條件判斷被移除，直接使用 `Some(ios_options.features)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/config.rs:253</code> reload_config 直接覆寫整個 ConfigMetadata 可能遺失未重新載入的欄位</summary>

`reload_config` 現在直接以 `*config = load_config(...)` 覆寫整個結構。若 `load_config` 在解析過程中因某些原因未能完整填入所有欄位（例如新增的欄位在舊版設定檔中不存在），可能導致原本存在於 `config` 中的值被清除。建議確認 `load_config` 是否保證完整重建所有欄位，或改為僅更新必要的部分。

**判斷依據**：diff 中 `reload_config` 的實作改為直接指派。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:131</code> resolve_dirs 使用 get_or_init 可能導致 panic 訊息不一致</summary>

`TAURI_DIR.get_or_init` 的初始化閉包中，若 `resolve_tauri_dir()` 回傳 `None`，會 panic。但 `FRONTEND_DIR.get_or_init` 的閉包中，若 `resolve_frontend_dir()` 回傳 `None`，會使用 `tauri.parent().unwrap()`，若 `tauri` 沒有 parent 也會 panic。這些 panic 訊息可能不如原本的 `expect` 明確，且 `get_or_init` 在初始化失敗時不會重試，可能導致後續呼叫永遠 panic。

**判斷依據**：diff 中 `resolve_dirs` 的實作。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36319 (cache hit 36224) ｜ completion tokens 1372 ｜ PR #5</sub>