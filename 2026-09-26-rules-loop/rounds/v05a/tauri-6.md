<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Android 平台新增返回鍵事件處理，包含 AppPlugin 實作、前端 API 與權限設定。主要風險在於 AppPlugin 的返回鍵處理邏輯：當無監聽器且 WebView 無法返回時，會暫時停用 callback 並呼叫 activity.onBackPressed()，可能造成遞迴或非預期行為；此外，AppPlugin 的 exit 命令未檢查 activity 是否為 AppCompatActivity，可能導致 ClassCastException。整體而言，功能方向正確，但需修正上述問題並補齊測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | AppPlugin 的返回鍵處理可能導致遞迴或非預期行為 | 0.90 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:50` | exit 命令未檢查 activity 型別，可能導致 ClassCastException | 0.80 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:21` | AppPlugin 未處理 webView 為 null 的情況 | 0.70 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:21` | AppPlugin 的 init 區塊可能過早執行 | 0.60 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:148` | AppPlugin 結構體缺少文件註解 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> AppPlugin 的返回鍵處理可能導致遞迴或非預期行為</summary>

在 `handleOnBackPressed` 中，當沒有監聽器且 WebView 無法返回時，程式碼會將 `this.isEnabled` 設為 false，呼叫 `activity.onBackPressed()`，然後再設回 true。然而，`activity.onBackPressed()` 會觸發系統的返回鍵處理，可能再次呼叫此 callback（若 callback 仍被註冊），造成遞迴。此外，若 `activity` 不是 `AppCompatActivity`，`onBackPressedDispatcher` 可能不存在，導致 NullPointerException。建議改用 `activity.onBackPressedDispatcher.onBackPressed()` 或直接呼叫 `activity.finish()`，並確保 activity 型別正確。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 29-31 行顯示此邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:50</code> exit 命令未檢查 activity 型別，可能導致 ClassCastException</summary>

`exit` 命令直接呼叫 `activity.finish()`，但 `activity` 在建構子中傳入，若實際型別不是 `Activity`（例如 `Context`），可能導致 ClassCastException。建議在建構子中檢查型別或使用更安全的方式取得 Activity。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 47-50 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:21</code> AppPlugin 未處理 webView 為 null 的情況</summary>

`webView` 屬性在 `load` 方法中賦值，但在 `handleOnBackPressed` 中直接使用 `this@AppPlugin.webView?.canGoBack()`，若 `load` 尚未被呼叫，`webView` 為 null，則 `canGoBack` 會回傳 null，導致後續邏輯錯誤。建議在 `handleOnBackPressed` 中檢查 `webView` 是否為 null，或確保 `load` 一定先被呼叫。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 15 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:21</code> AppPlugin 的 init 區塊可能過早執行</summary>

`init` 區塊在建構時執行，此時 `activity` 可能尚未完全初始化，且 `onBackPressedDispatcher` 可能尚未準備好。建議將 callback 註冊移至 `load` 方法或使用 `onCreate` 生命週期方法。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 21-22 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:148</code> AppPlugin 結構體缺少文件註解</summary>

根據專案規範 R07，公開 API 應包含文件註解。`AppPlugin` 結構體為 `pub(crate)`，但若未來公開，應補上文件。

**判斷依據**：diff 中新增的 plugin.rs 第 135 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33746 (cache hit 31744) ｜ completion tokens 1233 ｜ PR #6</sub>