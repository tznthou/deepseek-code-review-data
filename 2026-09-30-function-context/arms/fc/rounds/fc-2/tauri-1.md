<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 的 `generate_tauri_properties` 函式，並在 build 與 dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、檔案讀取失敗時靜默重置版本碼，以及移除 `tauri-build` 中的產生邏輯可能影響直接使用 `tauri-build` 的使用者。建議優先處理版本碼重置與競態問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增版本碼在並行建置時可能產生相同版本碼 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 讀取 `tauri.properties` 失敗時版本碼重置為 1 | 0.75 |
| ⚠️ | Major | `crates/tauri-build/src/mobile.rs:10` | 移除 `tauri-build` 中的 `tauri.properties` 產生邏輯可能破壞直接使用 `tauri-build` 的使用者 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 版本碼遞增使用 `saturating_add` 可能隱藏溢位 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增版本碼在並行建置時可能產生相同版本碼</summary>

`generate_tauri_properties` 讀取現有 `tauri.properties` 中的版本碼並加 1，但此讀取-修改-寫入並非原子操作。若兩個建置同時執行（例如 CI 中並行觸發），兩者可能讀到相同的舊版本碼，導致產生相同的 `versionCode`，造成 Google Play 上傳衝突。建議在建置前取得檔案鎖（例如使用既有的 `flock` 機制），或將版本碼儲存在支援原子遞增的儲存中。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式直接讀取檔案、計算新版本碼並寫回，沒有鎖定機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 讀取 `tauri.properties` 失敗時版本碼重置為 1</summary>

當 `auto_increment_version_code` 為 true 且 `tauri.properties` 不存在或無法讀取時，`last_version_code` 為 `None`，導致 `new_version_code` 被設為 1。這可能發生在首次建置或檔案被意外刪除時，造成版本碼回退，違反單調遞增要求，可能導致 Google Play 拒絕上傳。建議在無法讀取檔案時發出警告或錯誤，而非靜默重置。

**判斷依據**：diff 中 `unwrap_or(1)` 在讀取失敗時直接使用 1，沒有區分首次建置與錯誤情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-build/src/mobile.rs:10</code> 移除 `tauri-build` 中的 `tauri.properties` 產生邏輯可能破壞直接使用 `tauri-build` 的使用者</summary>

原本 `tauri-build` 的 `generate_gradle_files` 會根據設定產生 `tauri.properties`，現在此邏輯被移除，改由 CLI 在 build/dev 時呼叫 `generate_tauri_properties`。若使用者直接使用 `tauri-build`（例如在自訂建置腳本中呼叫 `tauri_build::try_build`）而不透過 CLI，將不再產生 `tauri.properties`，可能導致 Android 建置失敗或使用舊的版本碼。建議在 `tauri-build` 中保留此功能或提供明確的遷移指引。

**判斷依據**：diff 中 `generate_gradle_files` 的簽名從 `(project_dir, config)` 改為僅 `project_dir`，且移除了所有與 `tauri.properties` 相關的程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 版本碼遞增使用 `saturating_add` 可能隱藏溢位</summary>

當版本碼已達 `u32::MAX` 時，`saturating_add(1)` 會停留在最大值，不會產生錯誤。但 Android 版本碼上限為 2,100,000,000，若超過此值，Google Play 會拒絕。建議在遞增後檢查是否超過上限並回報錯誤。

**判斷依據**：diff 中使用 `saturating_add` 而非 `checked_add`，且未檢查結果是否超過 2,100,000,000。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10370 (cache hit 10368) ｜ completion tokens 1308 ｜ PR #1</sub>