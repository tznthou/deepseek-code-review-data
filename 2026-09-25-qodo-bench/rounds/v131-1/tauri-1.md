<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 Android 建置時自動遞增 versionCode 的設定選項，並將原本在 tauri-build 中產生 tauri.properties 的邏輯移至 tauri-cli 的 Android 建置流程。整體設計合理，但存在幾個需要修正的問題：自動遞增邏輯在並行建置時可能產生相同的 versionCode；當 versionCode 達到上限時會靜默飽和，可能導致上架失敗；此外，tauri-build 的函式簽名變更可能影響其他呼叫者，且缺少對新功能的測試。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 並行建置可能產生相同的 versionCode | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/src/mobile/android/mod.rs:645` | versionCode 達到上限時靜默飽和 | 0.70 |
| ⚠️ | Major | `crates/tauri-build/src/lib.rs:502` | 函式簽名變更可能影響其他呼叫者 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/mobile/android/mod.rs:636` | 缺少對新功能的測試 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 並行建置可能產生相同的 versionCode</summary>

在 `generate_tauri_properties` 中，讀取舊的 versionCode 後直接加 1 寫入，沒有使用鎖定或原子操作。如果兩個建置同時執行（例如 CI 中並行觸發），它們可能讀到相同的舊值，並產生相同的 versionCode，導致上架衝突。建議使用檔案鎖（例如 `flock`）或將 versionCode 儲存在可原子更新的位置（如資料庫或遠端服務）。

**判斷依據**：diff 中新增的程式碼直接讀取檔案並加 1，沒有同步機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:645</code> versionCode 達到上限時靜默飽和</summary>

使用 `saturating_add` 在 versionCode 達到 `u32::MAX` 時會停留在最大值，但 Android 的 versionCode 上限是 2100000000。如果超過此上限，Google Play 會拒絕上傳。建議在遞增前檢查是否超過上限，並提供明確的錯誤訊息。

**判斷依據**：diff 中新增的程式碼使用 `saturating_add`，沒有檢查 Android 的上限。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-build/src/lib.rs:502</code> 函式簽名變更可能影響其他呼叫者</summary>

`generate_gradle_files` 的簽名從 `(project_dir, &config)` 改為 `(project_dir)`，移除了 config 參數。如果其他 crate 或外部工具依賴此函式，將導致編譯錯誤。建議確認此函式是否為公開 API，並考慮保留向後相容性或更新所有呼叫者。

**判斷依據**：diff 中呼叫處的變更，以及函式定義的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/mobile/android/mod.rs:636</code> 缺少對新功能的測試</summary>

新增的自動遞增邏輯沒有對應的單元測試或整合測試。建議添加測試覆蓋以下情境：首次建置、正常遞增、檔案不存在、檔案格式錯誤、並行建置（如果實作鎖定）等。

**判斷依據**：diff 中新增的程式碼沒有對應的測試。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5849 (cache hit 1408) ｜ completion tokens 1164 ｜ PR #1</sub>