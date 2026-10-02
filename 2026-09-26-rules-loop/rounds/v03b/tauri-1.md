<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 的 `generate_tauri_properties`，並在 build/dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、錯誤處理，以及與既有 `version_code` 設定的互動。此外，移除 `tauri-build` 中的產生邏輯可能影響直接使用 `tauri-build` 的使用者。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件，可能導致重複的 versionCode | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 讀取 tauri.properties 失敗時靜默回退為 1，可能意外重置 versionCode | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 自動遞增時未檢查 versionCode 上限，可能產生無效值 | 0.70 |
| ⚠️ | Major | `crates/tauri-build/src/mobile.rs:10` | 移除 tauri-build 中的 tauri.properties 產生邏輯可能破壞直接使用 tauri-build 的使用者 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 自動遞增時未處理 versionCode 為 0 的情況 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件，可能導致重複的 versionCode</summary>

當 `auto_increment_version_code` 為 true 時，程式會讀取 `tauri.properties` 中的最後一個 versionCode 並加 1。若同時有多個建置程序（例如 CI 平行建置）執行，兩者可能讀到相同的值並寫入相同的遞增結果，導致 Google Play 上傳時發生 versionCode 衝突。建議使用檔案鎖或原子操作來確保遞增的獨佔性。

**判斷依據**：讀取與寫入之間沒有鎖定機制，且 `tauri.properties` 是共享檔案。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 讀取 tauri.properties 失敗時靜默回退為 1，可能意外重置 versionCode</summary>

若 `tauri.properties` 不存在或格式錯誤，`last_version_code` 會是 `None`，導致 `new_version_code` 被設為 1。這可能發生在檔案被誤刪或內容損壞時，造成 versionCode 從高值重置為 1，導致 Google Play 拒絕上傳。建議在讀取失敗時回報錯誤，或至少發出警告。

**判斷依據**：`.ok()` 將所有錯誤轉為 `None`，且 `unwrap_or(1)` 直接使用 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 自動遞增時未檢查 versionCode 上限，可能產生無效值</summary>

當 `auto_increment_version_code` 為 true 時，程式直接將讀取到的 versionCode 加 1，但未檢查是否超過 Android 允許的最大值 2100000000。若已達上限，`saturating_add` 會停留在 2100000000，但這仍可能無效。建議在遞增後檢查上限並回報錯誤。

**判斷依據**：沒有類似下方 semver 路徑中的 `version_code > 2100000000` 檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-build/src/mobile.rs:10</code> 移除 tauri-build 中的 tauri.properties 產生邏輯可能破壞直接使用 tauri-build 的使用者</summary>

原本 `tauri-build` 會根據設定產生 `tauri.properties`，現在此邏輯被移除，改由 CLI 在 build/dev 時呼叫。若使用者直接使用 `tauri-build`（例如在自訂建置腳本中），將不再產生此檔案，可能導致 Android 建置失敗。建議保留 `tauri-build` 中的產生邏輯，或提供明確的遷移指引。

**判斷依據**：函式簽名從 `generate_gradle_files(project_dir, &config)` 改為 `generate_gradle_files(project_dir)`，且移除了所有 `app_tauri_properties` 相關程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 自動遞增時未處理 versionCode 為 0 的情況</summary>

若 `tauri.properties` 中的 versionCode 為 0（可能由舊版產生），遞增後會變成 1，但這可能不是預期行為。建議在讀取後驗證值是否合法。

**判斷依據**：沒有對讀取到的 versionCode 進行範圍檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7977 (cache hit 7936) ｜ completion tokens 1497 ｜ PR #1</sub>