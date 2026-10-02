<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 的 `generate_tauri_properties` 函式，並在 build 與 dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、檔案讀取失敗時靜默重置為 1、以及移除 `tauri-build` 中的產生邏輯可能影響其他呼叫者。建議先處理競態與錯誤處理，並確認所有呼叫點都已更新。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 讀取 tauri.properties 失敗時靜默重置 versionCode 為 1 | 0.75 |
| ⚠️ | Major | `crates/tauri-build/src/mobile.rs:10` | 移除 tauri-build 中的 tauri.properties 產生邏輯可能影響其他呼叫者 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:652` | dev 模式下 versionCode 的 clamp 順序可能導致非預期結果 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件</summary>

`generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫回，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移到單一建置流程中，確保同一時間只有一個程序更新。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式，讀取與寫入之間沒有同步機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 讀取 tauri.properties 失敗時靜默重置 versionCode 為 1</summary>

當 `tauri.properties` 不存在或無法解析時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致在檔案遺失或格式錯誤時，版本碼意外重置，造成已發布的應用程式無法更新。建議在 `auto_increment_version_code` 為 true 且檔案不存在時，回傳錯誤或至少發出警告，而不是靜默重置。

**判斷依據**：diff 中該行直接使用 `unwrap_or(1)`，沒有區分檔案不存在與解析失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-build/src/mobile.rs:10</code> 移除 tauri-build 中的 tauri.properties 產生邏輯可能影響其他呼叫者</summary>

原本 `generate_gradle_files` 會根據 config 產生 `tauri.properties`，現在此邏輯被移除，改由 CLI 在 build/dev 時呼叫 `generate_tauri_properties`。但 `tauri-build` 是公開 crate，可能有其他使用者直接呼叫 `generate_gradle_files`，導致他們不再產生 `tauri.properties`，造成 Android 建置失敗。建議確認所有呼叫點都已更新，或保留向後相容的函式。

**判斷依據**：diff 中函式簽名從 `(project_dir, config)` 改為 `(project_dir)`，且移除了產生 `tauri.properties` 的程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:652</code> dev 模式下 versionCode 的 clamp 順序可能導致非預期結果</summary>

在 dev 模式下，程式先檢查 `version_code == 0` 和 `> 2100000000` 並回傳錯誤，然後才執行 `clamp(1, 2100000000)`。這表示如果 semver 計算出的 `version_code` 超過上限，dev 模式會直接失敗，而不是被 clamp 到上限。原本在 `tauri-build` 中的邏輯是先 clamp 再檢查，行為可能不一致。建議確認預期行為，並調整順序或移除重複檢查。

**判斷依據**：diff 中新增的程式碼片段，與被移除的 `tauri-build` 邏輯相比，順序不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5885 (cache hit 5760) ｜ completion tokens 1402 ｜ PR #1</sub>