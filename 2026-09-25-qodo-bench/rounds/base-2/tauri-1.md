<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 `autoIncrementVersionCode` 設定，將原本在 `tauri-build` 中產生 `tauri.properties` 的邏輯移至 CLI 的 `generate_tauri_properties` 函式，並在 build 與 dev 流程中呼叫。主要風險在於自動遞增邏輯的競態條件、錯誤處理，以及與既有 `version_code` 設定的互動。建議先修正 `generate_tauri_properties` 中的競態與錯誤處理，並確認 `tauri.properties` 的 gitignore 處理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 讀取 tauri.properties 失敗時靜默回退為 1 | 0.75 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:643` | 解析 versionCode 失敗時靜默回退為 1 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | saturating_add 可能導致版本碼停在最大值 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:652` | dev 模式下的 versionCode 計算順序可能導致非預期結果 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:680` | 寫入 tauri.properties 時未處理檔案不存在以外的錯誤 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:633` | generate_tauri_properties 未處理 version 為 None 的情況 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件</summary>

在 `generate_tauri_properties` 中，讀取 `tauri.properties` 取得 `last_version_code` 後直接加 1 寫回，但讀取與寫入之間沒有鎖定或原子操作。若同時執行多個 build（例如 CI 平行建置），可能導致多個 build 讀到相同的 `last_version_code`，產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移至單一進程中處理。

**判斷依據**：diff 中新增的 `generate_tauri_properties` 函式直接讀取檔案並計算新值，沒有鎖定機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 讀取 tauri.properties 失敗時靜默回退為 1</summary>

當 `std::fs::read_to_string` 失敗（例如檔案不存在或權限不足）時，程式會靜默地將 `new_version_code` 設為 1。這可能導致在檔案暫時無法讀取時意外重置版本碼，造成版本碼倒退。建議區分檔案不存在與其他錯誤：若檔案不存在，可視為首次建置；若為其他錯誤，應回報錯誤。

**判斷依據**：使用 `.ok()` 將所有讀取錯誤轉為 `None`，無法區分錯誤類型。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:643</code> 解析 versionCode 失敗時靜默回退為 1</summary>

若 `tauri.properties` 中的 `tauri.android.versionCode` 值不是有效的 `u32`（例如被手動修改或損壞），解析會失敗並回退為 1。這可能導致版本碼意外重置。建議在解析失敗時回報錯誤，或至少記錄警告。

**判斷依據**：使用 `.ok()` 忽略解析錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> saturating_add 可能導致版本碼停在最大值</summary>

使用 `saturating_add(1)` 在 `last_version_code` 已達 `u32::MAX` 時會停留在最大值，但 Android 的 `versionCode` 上限為 2100000000。若 `tauri.properties` 中的值已達上限，遞增後會超過限制，但此處未檢查。建議在遞增後檢查是否超過 2100000000，若超過則回報錯誤。

**判斷依據**：未對 `new_version_code` 進行上限檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:652</code> dev 模式下的 versionCode 計算順序可能導致非預期結果</summary>

在 `dev` 模式下，程式先檢查 `version_code` 是否為 0 或超過上限，然後才進行 `clamp(1, 2100000000)`。若原始 `version_code` 超過上限，會先觸發錯誤，但若原始值為 0，則會通過檢查後被 clamp 為 1。這與先前在 `tauri-build` 中的行為一致，但建議確認此順序是否符合預期。

**判斷依據**：diff 中顯示檢查與 clamp 的順序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:680</code> 寫入 tauri.properties 時未處理檔案不存在以外的錯誤</summary>

寫入 `tauri.properties` 時使用 `write`，若目錄不存在或權限不足會回傳錯誤，但錯誤訊息僅為「failed to write tauri.properties」，未包含路徑或更詳細的上下文。建議使用 `with_context` 加入路徑資訊。

**判斷依據**：錯誤訊息未包含路徑。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:633</code> generate_tauri_properties 未處理 version 為 None 的情況</summary>

若 `tauri_config.version` 為 `None`，函式不會產生任何內容，但也不會回報錯誤。這可能導致 `tauri.properties` 缺少必要的 `versionName` 和 `versionCode`，進而影響 Android 建置。建議確認 `version` 是否為必要欄位，若為必要則應在缺失時回報錯誤。

**判斷依據**：diff 中僅在 `version` 存在時才處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5885 (cache hit 5760) ｜ completion tokens 1947 ｜ PR #1</sub>