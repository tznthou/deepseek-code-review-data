<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 的 `generate_tauri_properties` 函式，並在 build/dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、檔案讀取失敗時靜默重置為 1，以及移除 `tauri-build` 中的版本檢查可能導致無效版本碼。建議先處理競態與錯誤處理，並確認版本碼上限。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 讀取失敗時靜默重置 versionCode 為 1 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 自動遞增時未檢查 versionCode 上限 | 0.70 |
| 🔸 | Minor | `crates/tauri-build/src/mobile.rs:10` | 移除 tauri-build 中的版本檢查可能導致無效版本碼 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件</summary>

`generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫入，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Google Play 上傳衝突。

建議：使用檔案鎖（如 `flock`）或將遞增邏輯移至建置系統中確保原子性。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式直接讀取檔案並加 1，沒有同步機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 讀取失敗時靜默重置 versionCode 為 1</summary>

當 `tauri.properties` 不存在或解析失敗時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致意外重置版本碼，尤其是在檔案被誤刪或格式錯誤時，造成 Google Play 上傳失敗。

建議：在無法讀取時發出警告或錯誤，或提供明確的 fallback 策略。

**判斷依據**：diff 中 `unwrap_or(1)` 在讀取失敗時直接使用 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 自動遞增時未檢查 versionCode 上限</summary>

當 `auto_increment_version_code` 為 true 時，直接使用 `saturating_add(1)`，但未檢查是否超過 Google Play 的 2100000000 上限。若已達上限，`saturating_add` 會停留在 2100000000，可能導致上傳失敗。

建議：在遞增後檢查上限，若超過則報錯。

**判斷依據**：diff 中未見上限檢查，且 `saturating_add` 可能隱藏溢位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-build/src/mobile.rs:10</code> 移除 tauri-build 中的版本檢查可能導致無效版本碼</summary>

原本在 `tauri-build` 中會檢查 semver 版本碼是否為 0 或超過上限，現在該邏輯移至 CLI 的 `generate_tauri_properties`，但 `tauri-build` 仍可能被單獨使用（例如非 CLI 建置）。若使用者直接呼叫 `tauri-build`，將不再有版本碼檢查，可能產生無效的 `tauri.properties`。

建議：保留 `tauri-build` 中的檢查，或確保所有建置路徑都經過 CLI。

**判斷依據**：diff 中 `generate_gradle_files` 簽名移除 `config` 參數，且刪除了版本檢查程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10370 (cache hit 1536) ｜ completion tokens 1226 ｜ PR #1</sub>