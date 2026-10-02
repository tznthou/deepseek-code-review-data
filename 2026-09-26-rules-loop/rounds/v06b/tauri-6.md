<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 Android 返回鍵事件處理，包含 Kotlin 外掛、Rust 端註冊、TypeScript API 及權限更新。主要風險在於 Kotlin 端 `handleOnBackPressed` 的邏輯：當沒有監聽器時，若 WebView 無法返回，會暫時停用 callback 並呼叫 `activity.onBackPressed()`，但 `onBackPressed()` 在 Android 13+ 已棄用且可能導致遞迴或行為不一致；此外，`webView` 屬性可能為 null 時使用 `!!` 有潛在 NPE 風險。整體功能方向正確，但需修正上述問題以確保穩定性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35` | 使用已棄用的 onBackPressed() 可能導致行為不一致或遞迴 | 0.85 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | webView 可能為 null 時使用 !! 導致 NPE | 0.80 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | OnBackPressedCallback 的 isEnabled 狀態管理可能造成事件遺漏 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35</code> 使用已棄用的 onBackPressed() 可能導致行為不一致或遞迴</summary>

在 `handleOnBackPressed` 中，當沒有監聽器且 WebView 無法返回時，程式碼呼叫 `this@AppPlugin.activity.onBackPressed()`。`Activity.onBackPressed()` 自 API 33 起已棄用，且在此情境下可能觸發系統預設行為（例如關閉 Activity），但由於此 callback 已攔截返回事件，可能造成非預期結果。建議改用 `onBackPressedDispatcher.onBackPressed()` 或直接呼叫 `activity.finish()`，並確保不會與 callback 邏輯衝突。

**判斷依據**：diff 中新增的 `handleOnBackPressed` 方法內，在 `else` 分支呼叫 `activity.onBackPressed()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> webView 可能為 null 時使用 !! 導致 NPE</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView!!.goBack()` 直接使用非空斷言。雖然 `load` 方法通常會在 callback 觸發前被呼叫，但若 WebView 尚未初始化或已被銷毀，可能拋出 NullPointerException。建議使用安全呼叫 `this@AppPlugin.webView?.goBack()` 並處理 null 情況。

**判斷依據**：diff 中 `handleOnBackPressed` 方法內，當 `canGoBack()` 為 true 時呼叫 `webView!!.goBack()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> OnBackPressedCallback 的 isEnabled 狀態管理可能造成事件遺漏</summary>

在沒有監聽器且 WebView 無法返回時，程式碼先將 `isEnabled` 設為 false，呼叫 `onBackPressed()` 後再設回 true。若 `onBackPressed()` 內部觸發非同步操作或導致 Activity 重建，可能使 callback 狀態不一致。建議考慮使用 `OnBackPressedCallback` 的 `setEnabled` 方法更精確地控制，或避免在 callback 內直接呼叫 `onBackPressed()`。

**判斷依據**：diff 中 `handleOnBackPressed` 方法內的三行程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33808 (cache hit 33792) ｜ completion tokens 908 ｜ PR #6</sub>