<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 端，並在 build/dev 流程中呼叫。主要風險在於自動遞增邏輯的競態與錯誤處理、檔案寫入時機、以及與既有 `version_code` 的互動。建議先確認併發建置情境與 `tauri.properties` 的讀寫一致性，再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件，可能導致多個建置取得相同版本碼 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 讀取 tauri.properties 失敗時靜默回退為 1，可能意外重置版本碼 | 0.75 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 版本碼遞增使用 saturating_add，可能靜默停在最大值 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:635` | 當 autoIncrementVersionCode 為 true 時，忽略手動設定的 version_code | 0.65 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:680` | 寫入 tauri.properties 前未建立目錄，可能導致失敗 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:625` | 公開函式 generate_tauri_properties 缺少文件註解 | 0.55 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:625` | 函式參數 dev 僅用於調整版本碼，但未在文件或命名中清楚表達 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件，可能導致多個建置取得相同版本碼</summary>

在 `generate_tauri_properties` 中，讀取舊的 `versionCode` 後直接加 1 並寫回，但讀取與寫入之間沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行觸發），兩者可能讀到相同的舊值，產生相同的 `versionCode`，導致 APK 上傳衝突或裝置無法升級。

建議：使用檔案鎖（例如 `fs2::FileExt::lock_exclusive`）或將版本碼儲存在具原子性的來源（如資料庫、Git tag），或至少加入重試機制。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式，讀取 `tauri.properties` 後立即計算新值並寫回，無任何同步機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 讀取 tauri.properties 失敗時靜默回退為 1，可能意外重置版本碼</summary>

當 `std::fs::read_to_string` 失敗（例如檔案不存在、權限不足）時，程式會將 `last_version_code` 設為 `None`，並將新版本碼設為 1。這可能導致在檔案暫時無法讀取時，版本碼被重置，造成已發布的 APK 版本碼倒退，違反 Android 版本碼必須遞增的規定。

建議：區分「檔案不存在」與其他 I/O 錯誤。若檔案不存在，可視為首次建置；若為其他錯誤，應回傳錯誤而非靜默回退。

**判斷依據**：使用 `.ok()` 將所有讀取錯誤轉為 `None`，未區分錯誤類型。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 版本碼遞增使用 saturating_add，可能靜默停在最大值</summary>

當 `last_version_code` 已達 `u32::MAX` 或接近時，`saturating_add(1)` 會停在最大值，不會產生錯誤。但 Android 版本碼上限為 2100000000，超過此值會導致建置失敗。此處未檢查新版本碼是否超過上限，可能讓使用者在上傳 APK 時才發現問題。

建議：在遞增後檢查是否超過 2100000000，若超過則回傳錯誤，或改用 `checked_add` 並處理溢位。

**判斷依據**：使用 `saturating_add` 而非 `checked_add`，且未檢查結果是否在合法範圍內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:635</code> 當 autoIncrementVersionCode 為 true 時，忽略手動設定的 version_code</summary>

在 `generate_tauri_properties` 中，若 `auto_increment_version_code` 為 true，則直接使用遞增後的版本碼，完全忽略 `tauri_config.bundle.android.version_code` 的設定。這可能讓使用者困惑，因為他們在設定檔中明確指定了版本碼，但實際產出的版本碼卻不同。

建議：在文件或錯誤訊息中明確說明此行為，或考慮在兩者衝突時發出警告。

**判斷依據**：條件分支中，若 `auto_increment_version_code` 為 true，則直接進入遞增邏輯，未檢查 `version_code` 是否存在。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:680</code> 寫入 tauri.properties 前未建立目錄，可能導致失敗</summary>

`app_tauri_properties_path` 位於 `project_dir/app/` 下，但程式碼中未確保該目錄存在。若目錄不存在，`write` 會失敗並回傳錯誤。雖然在正常流程中該目錄應已存在，但若使用者手動刪除或首次建置時未建立，可能導致建置失敗。

建議：在寫入前使用 `create_dir_all` 確保目錄存在。

**判斷依據**：直接呼叫 `write`，未先建立父目錄。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:625</code> 公開函式 generate_tauri_properties 缺少文件註解</summary>

此函式為 `pub`，但沒有 `///` 文件註解，違反專案規範 R07（Public APIs Must Include Documentation Comments）。這會降低 API 的可維護性，並可能導致文件產生工具遺漏此函式。

建議：新增文件註解，說明函式用途、參數與回傳值。

**判斷依據**：diff 中新增的 `pub fn generate_tauri_properties` 沒有文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:625</code> 函式參數 dev 僅用於調整版本碼，但未在文件或命名中清楚表達</summary>

`dev` 參數在函式中僅用於決定是否將版本碼 clamp 到 1..=2100000000，但從函式名稱與參數名稱無法直接理解其用途。這可能導致呼叫者誤用。

建議：在文件註解中說明 `dev` 的意義，或考慮將此邏輯拆分為獨立函式。

**判斷依據**：函式簽名中的 `dev` 參數未在名稱或文件中說明其用途。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7967 (cache hit 5760) ｜ completion tokens 2082 ｜ PR #1</sub>