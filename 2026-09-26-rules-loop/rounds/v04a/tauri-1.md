<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 層，並在 build/dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、錯誤處理不完整，以及既有 `version_code` 設定被忽略時的行為變更。建議先修正 `generate_tauri_properties` 中的錯誤處理與競態問題，並補齊測試。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件，可能導致重複的 versionCode | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 讀取 tauri.properties 失敗時靜默忽略，可能導致 versionCode 重置 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:635` | 當 auto_increment_version_code 為 true 時，忽略使用者設定的 version_code | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:625` | 缺少對 auto_increment_version_code 功能的測試 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:648` | 錯誤訊息不一致：使用 crate::error::bail! 而非 anyhow::bail! | 0.50 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 缺少對 versionCode 上限的檢查 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件，可能導致重複的 versionCode</summary>

在 `generate_tauri_properties` 中，讀取舊的 `versionCode` 並加 1 後寫回檔案，但此操作不是原子的。若多個 build 同時執行（例如 CI 中並行觸發），可能讀到相同的舊值，導致產生重複的 `versionCode`。這會造成 Android 應用程式無法上架或更新。

建議使用檔案鎖（例如 `fs2::FileExt::lock_exclusive`）或將 versionCode 儲存在具有原子更新機制的儲存中。

**判斷依據**：diff 中新增的程式碼直接讀取檔案、計算新值並寫回，沒有鎖定機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 讀取 tauri.properties 失敗時靜默忽略，可能導致 versionCode 重置</summary>

當 `auto_increment_version_code` 為 true 時，程式碼使用 `.ok()` 忽略讀取 `tauri.properties` 的錯誤。如果檔案不存在或讀取失敗，`last_version_code` 會是 `None`，導致 `new_version_code` 被設為 1。這可能造成 versionCode 從較大的值重置為 1，導致應用程式無法更新。

建議在讀取失敗時回傳錯誤，或至少記錄警告。

**判斷依據**：diff 中使用了 `.ok()` 來忽略讀取錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:635</code> 當 auto_increment_version_code 為 true 時，忽略使用者設定的 version_code</summary>

在 `generate_tauri_properties` 中，如果 `auto_increment_version_code` 為 true，則直接使用自動遞增的 versionCode，完全忽略 `tauri_config.bundle.android.version_code` 的設定。這可能不是使用者預期的行為，因為他們可能同時設定了兩者。

建議在文件或程式碼中明確說明優先順序，或考慮在兩者都設定時發出警告。

**判斷依據**：diff 中 `if` 分支直接處理自動遞增，沒有檢查 `version_code` 是否同時存在。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:625</code> 缺少對 auto_increment_version_code 功能的測試</summary>

新增的 `generate_tauri_properties` 函式包含複雜的邏輯（讀取檔案、解析、遞增、寫回），但沒有對應的單元測試。建議加入測試覆蓋各種情境，例如檔案不存在、格式錯誤、versionCode 已達上限等。

**判斷依據**：diff 中新增的函式沒有測試。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:648</code> 錯誤訊息不一致：使用 crate::error::bail! 而非 anyhow::bail!</summary>

在 `generate_tauri_properties` 中，錯誤處理使用了 `crate::error::bail!`，而其他部分可能使用 `anyhow::bail!`。這可能導致錯誤類型不一致，影響錯誤處理的統一性。建議確認專案慣例並保持一致。

**判斷依據**：diff 中使用了 `crate::error::bail!`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 缺少對 versionCode 上限的檢查</summary>

當 `auto_increment_version_code` 為 true 時，`new_version_code` 使用 `saturating_add(1)`，但沒有檢查是否超過 Android 允許的最大值 2100000000。如果超過，可能會導致建置失敗或產生無效的 versionCode。建議在遞增後檢查上限並回傳錯誤。

**判斷依據**：diff 中沒有對 `new_version_code` 進行上限檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6940 (cache hit 5760) ｜ completion tokens 1830 ｜ PR #1</sub>