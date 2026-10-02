<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以全域靜態變數（OnceLock）儲存的 Tauri 目錄、前端目錄與設定檔，改為在命令入口解析後以參數傳遞（Dirs、ConfigMetadata）。整體方向合理，可避免全域狀態帶來的測試與並行問題。但改動範圍極大，涉及多個命令與介面簽名，需特別注意：1) `resolve_dirs` 使用 `OnceLock` 仍保留全域快取，若不同命令在同一行程中需要不同路徑（例如測試或嵌入式使用）可能出錯；2) 多處將 `Mutex<ConfigMetadata>` 的 lock 結果直接傳遞，可能造成鎖定順序或生命週期問題；3) 部分函式簽名變更後，呼叫端未同步更新（如 `get_app` 的 `tauri_dir` 參數在 `mobile/mod.rs` 中重複宣告）。建議先修正上述問題，並確保所有平台（Windows/macOS/Linux）與行動端建置通過。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/helpers/app_paths.rs:130` | `resolve_dirs` 仍使用 `OnceLock` 全域快取，可能導致路徑解析錯誤 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/interface/rust.rs:595` | `reload_config` 與 `rewrite_manifest` 的鎖定順序可能導致死鎖或資料競爭 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/mod.rs:434` | `get_app` 函式內重複宣告 `tauri_dir` 變數，可能造成混淆或編譯錯誤 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/ios/mod.rs:272` | `features` 欄位從條件式改為直接 `Some(ios_options.features)`，可能改變行為 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/config.rs:74` | `fips_compliant` 使用 `var_os` 取代 `var`，可能導致非 UTF-8 值無法正確比對 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/app_paths.rs:130</code> `resolve_dirs` 仍使用 `OnceLock` 全域快取，可能導致路徑解析錯誤</summary>

`resolve_dirs` 內部使用 `TAURI_DIR.get_or_init` 與 `FRONTEND_DIR.get_or_init`，這兩個 `OnceLock` 是全域靜態變數。雖然函式回傳 `Dirs`，但實際上仍依賴全域狀態。若在同一個行程中，先以某個工作目錄呼叫 `resolve_dirs`，之後切換到另一個 Tauri 專案再呼叫，第二次呼叫會回傳第一次解析的結果，造成路徑錯誤。這在測試或嵌入式使用情境下特別危險。

建議：移除 `OnceLock`，改為每次呼叫都重新解析，或將 `Dirs` 的建立改為接受明確的基礎路徑參數，避免隱含的全域狀態。

**判斷依據**：diff 中 `resolve_dirs` 使用 `TAURI_DIR.get_or_init` 與 `FRONTEND_DIR.get_or_init`，這兩個變數仍為 `static` 的 `OnceLock`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/interface/rust.rs:595</code> `reload_config` 與 `rewrite_manifest` 的鎖定順序可能導致死鎖或資料競爭</summary>

在 `run_dev_watcher` 中，程式碼先對 `config` 的 `Mutex` 進行 `lock()`，然後呼叫 `reload_config(&mut config.lock().unwrap(), ...)`，接著又呼叫 `rewrite_manifest(&config.lock().unwrap(), ...)`。這會在同一個執行緒中多次鎖定同一個 `Mutex`，雖然 `std::sync::Mutex` 不是可重入的，但因為鎖定後立即解鎖（暫時的 guard 被丟棄），所以不會立即死鎖。然而，若 `reload_config` 內部在持有鎖定期間呼叫其他會嘗試鎖定同一個 `Mutex` 的函式，就可能造成死鎖。此外，將 `MutexGuard` 傳遞給其他函式可能導致生命週期問題。

建議：避免在鎖定範圍內呼叫可能再次鎖定的函式，或改用 `try_lock` 並處理錯誤。

**判斷依據**：diff 中 `reload_config` 與 `rewrite_manifest` 的呼叫都使用了 `config.lock().unwrap()`，且 `reload_config` 的第一個參數是 `&mut ConfigMetadata`，但傳入的是 `&mut config.lock().unwrap()`，這會建立一個暫時的 `MutexGuard`，並將其可變引用傳入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/mod.rs:434</code> `get_app` 函式內重複宣告 `tauri_dir` 變數，可能造成混淆或編譯錯誤</summary>

在 `get_app` 函式中，參數列已包含 `tauri_dir: &Path`，但函式內又使用 `let tauri_dir = tauri_dir.to_path_buf();` 重新宣告同名變數，遮蔽了參數。這可能導致後續程式碼使用到錯誤的變數（例如在 closure 中），且降低可讀性。

建議：將內部變數改名，例如 `let tauri_dir_buf = tauri_dir.to_path_buf();`，避免遮蔽。

**判斷依據**：diff 中 `get_app` 的參數列有 `tauri_dir: &Path`，但函式內又出現 `let tauri_dir = tauri_dir.to_path_buf();`，且後續使用 `tauri_dir.to_path_buf()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/ios/mod.rs:272</code> `features` 欄位從條件式改為直接 `Some(ios_options.features)`，可能改變行為</summary>

在 `get_config` 中，原本的程式碼是：
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
這表示即使 `features` 為空，也會傳入 `Some(vec![])`，而不是 `None`。這可能影響下游邏輯，例如某些程式碼會檢查 `features.is_none()` 來決定是否使用預設值。

建議：確認此變更是否為預期，並檢查所有使用 `features` 的地方是否正確處理空 `Some`。

**判斷依據**：diff 中原本的條件式被移除，改為直接 `Some(ios_options.features)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/config.rs:74</code> `fips_compliant` 使用 `var_os` 取代 `var`，可能導致非 UTF-8 值無法正確比對</summary>

原本的程式碼使用 `std::env::var("TAURI_BUNDLER_WIX_FIPS_COMPLIANT").ok().map(|v| v == "true")`，現在改為 `std::env::var_os(...).map(|v| v == "true")`。`var_os` 回傳 `OsString`，與 `"true"`（`&str`）比較時，若環境變數包含非 UTF-8 字元，比較結果可能不如預期。雖然此變數通常只會是 `"true"` 或 `"false"`，但使用 `var_os` 可能引入不必要的風險。

建議：若確定環境變數一定是 UTF-8，可繼續使用 `var`；否則應使用 `to_str()` 進行明確轉換。

**判斷依據**：diff 中 `var` 被改為 `var_os`，且比較對象為 `"true"`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 38401 (cache hit 38400) ｜ completion tokens 2098 ｜ PR #5</sub>