<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Android 建置時自動遞增 versionCode 的設定選項，並將原本在 tauri-build 中產生 tauri.properties 的邏輯移至 tauri-cli 的 Android 模組。主要風險在於自動遞增邏輯的競態條件、錯誤處理不足，以及與既有建置流程的相容性。建議先修正併發安全與錯誤處理問題，並確認文件與測試完整性。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 自動遞增 versionCode 存在競態條件 | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 自動遞增時未處理 versionCode 溢位 | 0.75 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 讀取 tauri.properties 失敗時靜默回退為 1 | 0.70 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:645` | 自動遞增時未驗證 versionCode 範圍 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:625` | 自動遞增邏輯未涵蓋所有建置路徑 | 0.50 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:680` | 未處理 tauri.properties 寫入失敗 | 0.40 |
| 🔸 | Minor | `crates/tauri-build/src/mobile.rs:10` | 移除 tauri.properties 產生邏輯可能影響既有使用者 | 0.30 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:2944` | 新增欄位未標記為 non_exhaustive | 0.20 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 自動遞增 versionCode 存在競態條件</summary>

在 `generate_tauri_properties` 中，讀取舊的 versionCode 並加 1 後寫回，但此操作不是原子的。若多個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 versionCode，造成 Android 套件衝突。建議使用檔案鎖（如 `flock`）或將 versionCode 儲存在具原子性的儲存機制中。

**判斷依據**：讀取與寫入之間沒有鎖定，且函式可能被多個程序同時呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 自動遞增時未處理 versionCode 溢位</summary>

使用 `saturating_add(1)` 避免溢位，但若 versionCode 已達最大值 2100000000，則會停留在最大值，導致後續建置產生相同 versionCode。應在溢位時回傳錯誤，提示使用者調整版本。

**判斷依據**：`saturating_add` 在達到上限時不會增加，且無錯誤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 讀取 tauri.properties 失敗時靜默回退為 1</summary>

當 `tauri.properties` 不存在或讀取失敗時，會直接從 1 開始，可能覆蓋已存在的 versionCode。若檔案因權限問題無法讀取，應回傳錯誤而非靜默重置。

**判斷依據**：使用 `.ok()` 忽略所有讀取錯誤，可能導致非預期的重置。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> 自動遞增時未驗證 versionCode 範圍</summary>

從檔案讀取的 versionCode 未檢查是否在 1 到 2100000000 之間。若檔案內容被手動修改為無效值，可能導致後續建置失敗。

**判斷依據**：未對讀取的值進行範圍驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:625</code> 自動遞增邏輯未涵蓋所有建置路徑</summary>

此邏輯僅在 `tauri android build` 和 `tauri android dev` 中呼叫，但若使用者直接執行 Gradle 建置，則不會觸發。應考慮整合至 Gradle 外掛或提供獨立指令。

**判斷依據**：僅在 CLI 命令中呼叫，未涵蓋直接 Gradle 建置。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:680</code> 未處理 tauri.properties 寫入失敗</summary>

寫入檔案時使用 `write` 並以 `context` 包裝錯誤，但若寫入失敗，函式會回傳錯誤，可能中斷建置。應考慮是否應回報警告而非失敗。

**判斷依據**：寫入失敗會導致整個建置失敗，可能過於嚴格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-build/src/mobile.rs:10</code> 移除 tauri.properties 產生邏輯可能影響既有使用者</summary>

原本在 `tauri-build` 中會產生 `tauri.properties`，現在移至 CLI。若使用者直接使用 `tauri-build` 而不透過 CLI，將不再產生該檔案，可能導致建置失敗。

**判斷依據**：函式簽名移除 `config` 參數，且不再寫入 `tauri.properties`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:2944</code> 新增欄位未標記為 non_exhaustive</summary>

`AndroidConfig` 是公開結構體，新增欄位可能導致下游使用結構體更新語法時出現破壞性變更。若專案允許，應考慮加上 `#[non_exhaustive]`。

**判斷依據**：公開結構體新增欄位，且未使用 `#[non_exhaustive]`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7967 (cache hit 7936) ｜ completion tokens 1740 ｜ PR #1</sub>