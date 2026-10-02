<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 Android 建置時自動遞增 versionCode 的設定選項，並將 tauri.properties 的產生邏輯從 tauri-build 移至 CLI。主要風險在於自動遞增邏輯的競態與錯誤處理、移除 tauri-build 中的產生邏輯可能影響既有使用者，以及新公開函式缺少文件。建議先處理併發與錯誤處理問題，並確認向後相容性。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件，可能導致重複的 versionCode | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 解析 tauri.properties 失敗時靜默回退為 1，可能造成版本倒退 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | saturating_add 可能導致 versionCode 超過上限而未偵測 | 0.70 |
| ⚠️ | Major | `crates/tauri-build/src/mobile.rs:10` | 移除 tauri-build 中的 tauri.properties 產生邏輯可能破壞既有使用者 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:625` | [R07] 公開函式 `generate_tauri_properties` 缺少文件註解 | 0.80 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 讀取 tauri.properties 時未處理檔案不存在以外的錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件，可能導致重複的 versionCode</summary>

在 `generate_tauri_properties` 中，讀取舊的 versionCode 與寫入新的 versionCode 之間沒有鎖定或原子操作。若同時執行多個建置（例如 CI 中平行觸發），可能讀到相同的舊值，導致產生重複的 versionCode。這會造成 Android 套件版本衝突，無法上架。建議使用檔案鎖（例如 `fs2::FileExt::lock_exclusive`）或將 versionCode 儲存在具原子性的來源（如資料庫），確保讀取與寫入的原子性。

**判斷依據**：diff 中新增的程式碼直接讀取檔案並計算新值，沒有鎖定機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 解析 tauri.properties 失敗時靜默回退為 1，可能造成版本倒退</summary>

當 `tauri.properties` 存在但內容格式錯誤（例如手動編輯、部分寫入）時，`parse::<u32>()` 會失敗，導致 `last_version_code` 為 `None`，新版本碼會從 1 開始。這可能造成 versionCode 倒退，導致安裝失敗或無法更新。建議在解析失敗時回傳錯誤，或至少記錄警告，避免靜默回退。

**判斷依據**：使用 `.ok()` 忽略所有錯誤，且 `unwrap_or(1)` 在解析失敗時直接使用 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> saturating_add 可能導致 versionCode 超過上限而未偵測</summary>

當舊的 versionCode 已達 `u32::MAX` 或接近上限時，`saturating_add(1)` 會停留在最大值，不會產生錯誤。但 Android 的 versionCode 上限為 2100000000，超過會導致建置失敗。此處未檢查新值是否超過上限，可能在使用者未察覺的情況下產生無效的 versionCode。建議在遞增後檢查是否超過 2100000000，並回傳錯誤。

**判斷依據**：使用 `saturating_add` 避免溢位，但未檢查 Android 上限。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-build/src/mobile.rs:10</code> 移除 tauri-build 中的 tauri.properties 產生邏輯可能破壞既有使用者</summary>

原本 `tauri-build` 在建置時會產生 `tauri.properties`，現在改由 CLI 在建置前呼叫 `generate_tauri_properties`。若使用者直接使用 `tauri-build` 而不透過 CLI（例如自訂建置流程），將不再產生該檔案，可能導致 Android 建置失敗。建議保留 `tauri-build` 中的產生邏輯作為向後相容，或提供明確的遷移指引。

**判斷依據**：diff 中移除了 `generate_gradle_files` 中產生 `tauri.properties` 的程式碼，且函式簽名不再接收 `config`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:625</code> [R07] 公開函式 `generate_tauri_properties` 缺少文件註解</summary>

此函式為 `pub`，但沒有 `///` 文件註解，違反專案規範 R07。建議補充說明函式的用途、參數與回傳值。

**判斷依據**：diff 中新增的函式沒有文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 讀取 tauri.properties 時未處理檔案不存在以外的錯誤</summary>

使用 `std::fs::read_to_string(...).ok()` 會忽略所有 I/O 錯誤，包括權限不足、檔案損毀等。這可能導致在無法讀取檔案時靜默回退為 1，造成版本倒退。建議區分檔案不存在與其他錯誤，並在後者時回傳錯誤。

**判斷依據**：使用 `.ok()` 忽略所有錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7977 (cache hit 5760) ｜ completion tokens 1694 ｜ PR #1</sub>