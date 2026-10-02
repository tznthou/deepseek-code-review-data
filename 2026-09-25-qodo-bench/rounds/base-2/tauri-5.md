<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本全域靜態的 app paths 與 config 改為以參數傳遞的 Dirs 與 ConfigMetadata，大幅減少全域狀態。整體方向正確，但涉及大量函式簽名變更，需特別注意併發與生命週期問題。最關鍵的風險在於 `resolve_dirs()` 回傳的 `Dirs` 持有 `&'static Path`，但實際指向 `OnceLock` 中的 `PathBuf`，若未來重新初始化可能導致懸垂指標；此外，`dev` 流程中將 `ConfigMetadata` 包在 `Mutex` 後傳入 watcher，需確認鎖定順序與重新載入邏輯不會造成死結或資料競爭。建議優先修正 `Dirs` 的生命週期設計，並補齊相關測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/helpers/app_paths.rs:26` | Dirs 結構體持有 &'static Path 可能造成懸垂指標 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/interface/rust.rs:595` | 在 watcher 中鎖定 config Mutex 可能導致死結或長時間阻塞 | 0.75 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/config.rs:247` | reload_config 直接覆寫整個 ConfigMetadata 可能遺失未儲存的變更 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/ios/mod.rs:272` | iOS 設定中 features 欄位從條件式改為一律 Some，可能改變行為 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:26</code> Dirs 結構體持有 &'static Path 可能造成懸垂指標</summary>

`Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但實際值是從 `OnceLock<PathBuf>` 中取得的參考。雖然目前 `OnceLock` 只會被初始化一次，但若未來程式碼在 `resolve_dirs()` 之後再次呼叫 `TAURI_DIR.set(...)` 或 `FRONTEND_DIR.set(...)`（例如在測試或重設邏輯中），舊的 `Dirs` 實例將持有指向已釋放記憶體的懸垂指標。建議改為持有 `PathBuf` 或使用 `Arc<Path>` 來確保生命週期安全。

**判斷依據**：diff 中新增的 `Dirs` 結構體直接使用 `&'static Path`，而 `resolve_dirs()` 透過 `TAURI_DIR.get_or_init(...)` 取得參考，該參考的生命週期受限於 `OnceLock` 的內容，並非真正的 `'static`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> 在 watcher 中鎖定 config Mutex 可能導致死結或長時間阻塞</summary>

在 `run_dev_watcher` 中，當偵測到設定檔變更時，程式碼執行 `reload_config(&mut config.lock().unwrap(), merge_configs, dirs.tauri)`。此處直接對 `config` 的 `Mutex` 進行鎖定，若同時間有其他執行緒（例如 `dev` 流程中的其他部分）也持有該鎖，可能導致阻塞。此外，`reload_config` 內部會重新載入設定並可能觸發其他操作，若在鎖定期間發生 panic，可能導致 poison。建議縮小鎖定範圍，或使用 `try_lock` 並處理失敗情況。

**判斷依據**：diff 中新增的 watcher 邏輯直接呼叫 `config.lock().unwrap()`，且 `reload_config` 可能執行較長時間（讀取檔案、解析等），增加鎖定競爭風險。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/config.rs:247</code> reload_config 直接覆寫整個 ConfigMetadata 可能遺失未儲存的變更</summary>

`reload_config` 函式直接將 `*config = load_config(...)` 的結果指派給傳入的 `&mut ConfigMetadata`。若在重新載入前有其他程式碼修改了 `config` 的某些欄位（例如透過 `merge_config_with`），這些變更會在重新載入時被覆蓋。建議先合併現有變更再重新載入，或明確區分唯讀與可變部分。

**判斷依據**：diff 中 `reload_config` 的實作直接指派新值，未保留任何現有狀態。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/ios/mod.rs:272</code> iOS 設定中 features 欄位從條件式改為一律 Some，可能改變行為</summary>

在 `get_config` 中，原本 `features` 欄位在 `ios_options.features` 為空時設為 `None`，現在改為一律 `Some(ios_options.features)`。這可能導致下游程式碼在處理 `None` 與 `Some(空 Vec)` 時有不同的行為，例如序列化或條件判斷。建議確認此變更是否為預期，並檢查所有使用該欄位的地方。

**判斷依據**：diff 中刪除了原本的條件判斷，直接使用 `Some(ios_options.features)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 36319 (cache hit 36224) ｜ completion tokens 1395 ｜ PR #5</sub>