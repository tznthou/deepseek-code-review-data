<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 Android 返回鍵事件處理，包含 Kotlin 外掛、Rust 端註冊、TypeScript API 及權限設定。主要風險在於 Kotlin 外掛中對 WebView 的強制非空斷言可能導致 NPE、返回鍵處理邏輯與既有導航行為的互動，以及缺少對應測試。建議先修正 NPE 風險並補充測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | 強制非空斷言可能導致 NullPointerException | 0.80 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | 返回鍵處理可能干擾既有導航行為 | 0.70 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:42` | 缺少對返回鍵事件的測試 | 0.60 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:138` | Android 外掛註冊缺少錯誤處理 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> 強制非空斷言可能導致 NullPointerException</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView!!.goBack()` 使用了強制非空斷言。雖然前面有 `canGoBack()` 檢查，但 `webView` 屬性可能尚未初始化（例如 `load()` 未被呼叫），此時會拋出 NPE。建議改用安全呼叫或延遲初始化。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 30 行，`webView` 宣告為 `private var webView: WebView? = null`，在 `load()` 中才賦值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> 返回鍵處理可能干擾既有導航行為</summary>

當沒有監聽器且 WebView 無法返回時，程式碼會停用 callback、呼叫 `activity.onBackPressed()`，再重新啟用。這可能導致 Activity 的預設返回行為被觸發兩次或與其他 callback 衝突。建議確認此流程與 AndroidX 的 `OnBackPressedDispatcher` 整合方式。

**判斷依據**：diff 中 AppPlugin.kt 第 34-36 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:42</code> 缺少對返回鍵事件的測試</summary>

新增的返回鍵處理邏輯沒有對應的單元測試或儀器測試。建議至少測試有監聽器與無監聽器時的行為，以及 WebView 可返回與不可返回的情境。

**判斷依據**：diff 中未包含任何測試檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:138</code> Android 外掛註冊缺少錯誤處理</summary>

`register_android_plugin` 回傳 `Result`，但使用 `?` 直接傳播錯誤。若註冊失敗，整個 plugin 初始化會失敗，可能導致應用程式無法啟動。建議考慮記錄錯誤並繼續，或提供更明確的錯誤訊息。

**判斷依據**：diff 中 plugin.rs 第 139 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 32791 (cache hit 32768) ｜ completion tokens 891 ｜ PR #6</sub>