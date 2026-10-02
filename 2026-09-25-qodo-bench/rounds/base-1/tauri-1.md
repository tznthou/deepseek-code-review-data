<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 `autoIncrementVersionCode` 設定，將原本在 build script 中產生 `tauri.properties` 的邏輯移至 CLI 的 `generate_tauri_properties` 函式，並在 build 與 dev 流程中呼叫。主要風險在於自動遞增邏輯的實作：讀取既有 versionCode 時若檔案不存在或格式不符會從 1 開始，可能導致版本碼倒退；且並未檢查遞增後是否超過 Android 上限 2100000000。此外，`tauri.properties` 的寫入時機與 `.gitignore` 的互動可能造成 CI 中版本碼不一致。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 自動遞增 versionCode 可能超過上限或倒退 | 0.80 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 自動遞增時未處理 versionCode 為 0 的情況 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:630` | 寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 自動遞增 versionCode 可能超過上限或倒退</summary>

當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式內，`last_version_code` 從檔案讀取，若讀取失敗或無此 key 則 `unwrap_or(1)`，且 `saturating_add` 不會回報溢位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 自動遞增時未處理 versionCode 為 0 的情況</summary>

若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

**判斷依據**：diff 中未對 `last_version_code` 做範圍檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:630</code> 寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致</summary>

`generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

**判斷依據**：diff 中新增的函式直接讀寫該路徑，但未檢查檔案是否存在或是否被版本控制忽略。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5885 (cache hit 1536) ｜ completion tokens 930 ｜ PR #1</sub>