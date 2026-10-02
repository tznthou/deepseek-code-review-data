<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 層，並在 build/dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、錯誤處理，以及移除 `tauri-build` 中的產生邏輯可能造成的相容性問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 讀取 tauri.properties 失敗時靜默回退為 1 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | versionCode 可能超過 Android 上限 | 0.70 |
| ⚠️ | Major | `crates/tauri-build/src/mobile.rs:10` | 移除 tauri-build 中的 tauri.properties 產生邏輯可能破壞下游使用者 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/build.rs:181` | 在 build 流程中呼叫 generate_tauri_properties 可能重複寫入 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:680` | 未處理 tauri.properties 寫入失敗的錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件</summary>

當 `auto_increment_version_code` 為 true 時，程式讀取現有 `tauri.properties` 中的 versionCode 並加 1。若多個 build 同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 versionCode，造成 Android 套件衝突。建議加入檔案鎖或使用原子操作。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式，讀取與寫入之間沒有同步機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 讀取 tauri.properties 失敗時靜默回退為 1</summary>

若 `tauri.properties` 存在但內容格式錯誤（例如 versionCode 非數字），程式會忽略錯誤並從 1 開始，可能導致 versionCode 倒退，造成安裝失敗。建議在解析失敗時回報錯誤或保留舊值。

**判斷依據**：使用 `.ok()` 和 `.and_then` 鏈，任何失敗都會變成 `None`，最後 `unwrap_or(1)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> versionCode 可能超過 Android 上限</summary>

自動遞增時使用 `saturating_add`，若舊值已達 `u32::MAX` 或接近上限，加 1 後可能超過 2100000000，但沒有檢查。建議在遞增後檢查是否超過上限並回報錯誤。

**判斷依據**：diff 中新增的程式碼沒有對 `new_version_code` 做範圍驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-build/src/mobile.rs:10</code> 移除 tauri-build 中的 tauri.properties 產生邏輯可能破壞下游使用者</summary>

原本 `tauri-build` 會根據 config 產生 `tauri.properties`，現在完全移除。若使用者直接呼叫 `tauri-build` 而不透過 CLI，將不再產生該檔案，可能導致建置失敗。建議保留相容性或在文件中說明。

**判斷依據**：diff 中刪除了原本產生 `tauri.properties` 的程式碼，且函式簽名移除 `config` 參數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/build.rs:181</code> 在 build 流程中呼叫 generate_tauri_properties 可能重複寫入</summary>

`generate_tauri_properties` 在 build 和 dev 流程中都被呼叫，若兩者同時執行可能互相覆蓋。建議確認呼叫時機是否正確，或加入鎖定機制。

**判斷依據**：diff 中新增的呼叫，且 dev 流程也有類似呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:680</code> 未處理 tauri.properties 寫入失敗的錯誤</summary>

寫入 `tauri.properties` 時使用 `write` 並以 `context` 包裝錯誤，但若寫入失敗，函式會回傳錯誤，可能導致 build 中斷。建議考慮是否應忽略寫入失敗或提供更明確的錯誤訊息。

**判斷依據**：diff 中新增的寫入邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6940 (cache hit 6912) ｜ completion tokens 1478 ｜ PR #1</sub>