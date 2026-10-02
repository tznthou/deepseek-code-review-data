<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 端，並在 build/dev 流程中呼叫。主要風險在於自動遞增邏輯的競態與錯誤處理：讀取與寫入 `tauri.properties` 之間沒有鎖定，並行建置可能產生相同的 versionCode；且當檔案內容格式不符預期時，會靜默回退為 1，可能導致版本碼倒退。此外，移除 `tauri-build` 中的產生邏輯可能影響直接使用 `tauri-build` 的使用者。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件，並行建置可能產生重複版本碼 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 解析 `tauri.properties` 失敗時靜默回退為 1，可能導致版本碼倒退 | 0.70 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:640` | 移除 `tauri-build` 中的產生邏輯可能破壞直接使用 `tauri-build` 的使用者 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | `saturating_add` 可能導致 versionCode 停在最大值，而非報錯 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 未驗證 `tauri.properties` 中的 versionCode 是否為有效範圍 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件，並行建置可能產生重複版本碼</summary>

`generate_tauri_properties` 在讀取 `tauri.properties` 中的舊 versionCode 後，直接寫入遞增後的值，中間沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 中並行觸發），兩者可能讀到相同的舊值，並寫入相同的遞增結果，導致產生重複的 versionCode，造成 Android 套件衝突。

建議：在讀取與寫入之間加入檔案鎖（例如使用 `fs2::FileExt::lock_exclusive`），或將 versionCode 的產生與更新改為原子操作。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式，在讀取 `tauri.properties` 後直接寫入，無鎖定機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 解析 `tauri.properties` 失敗時靜默回退為 1，可能導致版本碼倒退</summary>

當 `tauri.properties` 存在但內容格式不符（例如手動編輯錯誤、檔案損毀），`read_to_string` 成功但解析失敗，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致 versionCode 從較大值倒退為 1，造成 Android 安裝衝突（新版本無法覆蓋舊版本）。

建議：解析失敗時應回傳錯誤，或至少記錄警告，而不是靜默使用 1。

**判斷依據**：diff 中 `last_version_code` 的解析鏈使用 `.ok()` 吞掉所有錯誤，且 `unwrap_or(1)` 在解析失敗時直接使用 1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:640</code> 移除 `tauri-build` 中的產生邏輯可能破壞直接使用 `tauri-build` 的使用者</summary>

原本 `tauri-build` 的 `generate_gradle_files` 會根據設定產生 `tauri.properties`，現在此邏輯被移除，改由 CLI 在 build/dev 時呼叫。若使用者直接使用 `tauri-build`（例如在自訂建置腳本中呼叫 `tauri_build::try_build`），將不再產生 `tauri.properties`，可能導致 Android 建置缺少必要的版本資訊。

建議：確認 `tauri-build` 是否為公開 API，若是，應保留向後相容的產生邏輯，或提供明確的遷移指引。

**判斷依據**：diff 中 `generate_gradle_files` 的簽名從 `(project_dir, config)` 改為 `(project_dir)`，且移除了所有與 `tauri.properties` 相關的程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> `saturating_add` 可能導致 versionCode 停在最大值，而非報錯</summary>

當 `last_version_code` 已達 `u32::MAX`（或接近），`saturating_add(1)` 會停在最大值，不會溢位，但也不會觸發錯誤。這可能導致 versionCode 無法繼續遞增，且使用者不會收到任何警告。

建議：在遞增前檢查是否已達上限，若已達上限應回傳錯誤。

**判斷依據**：diff 中使用 `saturating_add` 進行遞增，未處理已達上限的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 未驗證 `tauri.properties` 中的 versionCode 是否為有效範圍</summary>

從 `tauri.properties` 讀取的 versionCode 未檢查是否在 1 到 2100000000 之間。若檔案中已有無效值（例如手動修改），遞增後仍可能超出範圍，導致後續建置失敗。

建議：在讀取後驗證範圍，若無效則回傳錯誤或採取其他處理。

**判斷依據**：diff 中解析出的 `last_version_code` 未進行範圍驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7967 (cache hit 7936) ｜ completion tokens 1797 ｜ PR #1</sub>