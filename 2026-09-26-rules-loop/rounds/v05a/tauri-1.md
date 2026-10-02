<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 的 `generate_tauri_properties` 函式，並在 build 與 dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、錯誤處理與既有行為的相容性。最需優先處理的是 `generate_tauri_properties` 中讀取與寫入 `tauri.properties` 的競態，以及 `autoIncrementVersionCode` 啟用時可能覆蓋手動設定的 `versionCode`。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:635` | autoIncrementVersionCode 啟用時忽略手動設定的 versionCode | 0.75 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | saturating_add 可能導致 versionCode 停在最大值 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:652` | dev 模式下 versionCode 的 clamp 邏輯可能造成非預期結果 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:625` | generate_tauri_properties 函式缺少文件註解 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:625` | generate_tauri_properties 函式名稱與模組結構可能造成混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件</summary>

在 `generate_tauri_properties` 中，讀取 `tauri.properties` 取得 `last_version_code` 後，直接寫入新的 `versionCode`。若同時有多個建置程序（例如平行 CI 或開發者同時執行），可能讀到相同的舊值，導致最終寫入相同的 `versionCode`，造成版本衝突。

建議：使用檔案鎖（例如 `flock`）或原子寫入（寫入暫存檔後 rename）來確保讀取與寫入的原子性。

**判斷依據**：讀取與寫入之間沒有同步機制，且函式可能被多個程序同時呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:635</code> autoIncrementVersionCode 啟用時忽略手動設定的 versionCode</summary>

當 `auto_increment_version_code` 為 `true` 時，程式直接從 `tauri.properties` 讀取舊值並遞增，完全忽略 `tauri_config.bundle.android.version_code` 的設定。這可能導致使用者設定的 `versionCode` 被覆蓋，且行為與文件描述（「If `true`, the generator will try to read the last `versionCode` from `tauri.properties` and increment it by 1 for every build.」）一致，但可能不符合使用者預期。

建議：在文件中明確說明此行為，或考慮提供合併策略（例如以手動設定為基礎遞增）。

**判斷依據**：此分支完全未使用 `tauri_config.bundle.android.version_code`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> saturating_add 可能導致 versionCode 停在最大值</summary>

使用 `saturating_add(1)` 在 `u32` 最大值時不會溢位，但會停留在 `u32::MAX`，而 Android 的 `versionCode` 上限為 2100000000。若 `last_version_code` 已達上限，遞增後仍超過上限，但程式不會報錯，可能導致後續建置失敗。

建議：在遞增後檢查是否超過 2100000000，若超過則回傳錯誤。

**判斷依據**：未檢查 `new_version_code` 是否超過 2100000000。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:652</code> dev 模式下 versionCode 的 clamp 邏輯可能造成非預期結果</summary>

在 dev 模式下，若 semver 計算出的 `version_code` 超過 2100000000，會先檢查並回傳錯誤，然後才進行 `clamp(1, 2100000000)`。這表示 dev 模式下仍會因版本過大而失敗，與先前 `tauri-build` 的行為（先 clamp 再檢查）不同。

建議：確認此行為變更是否為預期，並考慮在 dev 模式下先 clamp 再檢查。

**判斷依據**：檢查順序與先前實作不同，可能影響 dev 模式下的行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:625</code> generate_tauri_properties 函式缺少文件註解</summary>

此函式為公開函式（`pub fn`），但沒有文件註解。根據專案規範 R07，公開 API 應包含文件註解。

建議：新增 `///` 文件說明函式用途、參數與回傳值。

**判斷依據**：函式宣告前沒有文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:625</code> generate_tauri_properties 函式名稱與模組結構可能造成混淆</summary>

函式位於 `mobile::android` 模組中，但名稱未明確指出與 Android 相關。建議更名為 `generate_android_tauri_properties` 或類似名稱，以提高可讀性。

**判斷依據**：函式名稱未包含 `android` 字樣。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7895 (cache hit 5888) ｜ completion tokens 1988 ｜ PR #1</sub>