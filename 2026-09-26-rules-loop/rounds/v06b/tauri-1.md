<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 的 `generate_tauri_properties`，並在 build/dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、錯誤處理，以及與既有 `version_code` 設定的互動。建議先處理 `generate_tauri_properties` 中的競態與錯誤處理，再考慮合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件，可能導致重複的 versionCode | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 讀取 tauri.properties 失敗時靜默忽略，可能導致 versionCode 重置 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 自動遞增時未檢查 versionCode 上限，可能產生無效值 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:635` | 自動遞增與手動 version_code 同時設定時，自動遞增優先，可能非預期 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:625` | generate_tauri_properties 函式缺少文件註解 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件，可能導致重複的 versionCode</summary>

`generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫入，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 中並行觸發），兩者可能讀到相同的舊值，產生相同的 `versionCode`，導致 Google Play 上傳衝突。

建議：使用檔案鎖（例如 `flock`）或將遞增邏輯移到建置系統中，確保原子性。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式，讀取與寫入之間沒有鎖定機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 讀取 tauri.properties 失敗時靜默忽略，可能導致 versionCode 重置</summary>

當 `std::fs::read_to_string` 失敗（例如檔案不存在或權限不足）時，程式碼使用 `.ok()` 忽略錯誤，並將 `last_version_code` 設為 `None`，導致 `new_version_code` 從 1 開始。這可能意外重置 versionCode，造成 Google Play 上傳失敗。

建議：區分檔案不存在與其他錯誤，檔案不存在時可從 1 開始，其他錯誤應回報。

**判斷依據**：diff 中 `.ok()` 吞掉所有 I/O 錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 自動遞增時未檢查 versionCode 上限，可能產生無效值</summary>

當 `auto_increment_version_code` 為 true 時，程式碼直接使用 `saturating_add(1)`，但未檢查結果是否超過 Android 允許的最大值 2100000000。若已達上限，saturating_add 會停留在 2100000000，導致重複的 versionCode。

建議：在遞增後檢查是否超過上限，若超過則回報錯誤。

**判斷依據**：diff 中未對 `new_version_code` 進行上限檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:635</code> 自動遞增與手動 version_code 同時設定時，自動遞增優先，可能非預期</summary>

當 `auto_increment_version_code` 為 true 且 `version_code` 也有設定時，程式碼會忽略手動設定的 `version_code`，直接使用自動遞增。這可能讓使用者困惑，因為設定檔中明確指定了 versionCode 卻被忽略。

建議：在文件或錯誤訊息中明確說明優先順序，或當兩者同時設定時發出警告。

**判斷依據**：diff 中 `auto_increment_version_code` 分支優先於 `version_code` 分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:625</code> generate_tauri_properties 函式缺少文件註解</summary>

此函式為公開函式，但沒有文件註解，違反專案規範 R07。建議加上說明其用途、參數與回傳值。

**判斷依據**：diff 中新增的公開函式沒有 `///` 文件。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7957 (cache hit 7936) ｜ completion tokens 1411 ｜ PR #1</sub>