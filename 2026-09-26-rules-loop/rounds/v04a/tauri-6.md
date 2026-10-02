<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Android 平台新增返回鍵事件處理，包含 Kotlin 插件、Rust 端註冊、TypeScript API 及權限更新。主要風險在於 AppPlugin 的返回鍵處理邏輯：當無監聽器時，若 WebView 無法回退則直接呼叫 activity.onBackPressed()，可能導致非預期的 Activity 結束；此外，hasListener 的實作依賴 listeners 結構，需確認其正確性。另有部分程式碼風格與文件問題。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35` | 無監聽器時直接呼叫 onBackPressed 可能導致非預期關閉 | 0.80 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | 使用 `!!` 強制解包可能導致 NullPointerException | 0.70 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:135` | 使用 `_app` 和 `_api` 作為變數名稱不符合慣例 | 0.70 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46` | 缺少對 `activity` 是否為 `AppCompatActivity` 的檢查 | 0.60 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:148` | `AppPlugin` 結構體缺少文件註解 | 0.60 |
| 🔸 | Minor | `packages/api/src/app.ts:258` | 型別 `OnBackButtonPressPayload` 未匯出為公開 API | 0.60 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:5` | 缺少版權和 SPDX 標頭 | 0.50 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:14` | 未使用的 import `Invoke` 和 `JSObject` | 0.50 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/plugin/Plugin.kt:149` | `hasListener` 方法缺少文件註解 | 0.50 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:138` | `register_android_plugin` 的回傳值未處理錯誤 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35</code> 無監聽器時直接呼叫 onBackPressed 可能導致非預期關閉</summary>

當沒有註冊 `back-button` 監聽器且 WebView 無法回退時，程式碼直接呼叫 `activity.onBackPressed()`。這會觸發 Activity 的預設返回行為，通常是結束 Activity。若此 Activity 是應用的主要 Activity，應用程式將被關閉，可能不符合使用者預期。建議改為呼叫 `activity.finish()` 或提供明確的退出機制，並考慮與前端溝通。

**判斷依據**：diff 中 AppPlugin.kt 第 30 行附近：`this@AppPlugin.activity.onBackPressed()`

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> 使用 `!!` 強制解包可能導致 NullPointerException</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView!!.goBack()` 使用了非空斷言。雖然 `webView` 在 `load` 中賦值，但若 `load` 未被呼叫或時序問題，可能為 null，導致崩潰。建議使用安全呼叫或檢查 null。

**判斷依據**：diff 中 AppPlugin.kt 第 26 行附近：`this@AppPlugin.webView!!.goBack()`

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:135</code> 使用 `_app` 和 `_api` 作為變數名稱不符合慣例</summary>

在 `setup` 閉包中，參數命名為 `_app` 和 `_api`，但實際上都有使用。Rust 慣例中，以底線開頭表示未使用，此處會造成混淆。建議改名為 `app` 和 `api`。

**判斷依據**：diff 中 plugin.rs 第 135 行附近：`.setup(|_app, _api| {`

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46</code> 缺少對 `activity` 是否為 `AppCompatActivity` 的檢查</summary>

在建構子中直接將 `activity` 轉型為 `AppCompatActivity`，若傳入的 Activity 不是 `AppCompatActivity` 會拋出 `ClassCastException`。建議在註冊插件時確保 Activity 類型，或使用更安全的方式取得 `OnBackPressedDispatcher`。

**判斷依據**：diff 中 AppPlugin.kt 第 20 行附近：`(activity as AppCompatActivity).onBackPressedDispatcher.addCallback(activity, callback)`

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:148</code> `AppPlugin` 結構體缺少文件註解</summary>

新增的 `AppPlugin` 結構體是公開的（`pub(crate)`），但沒有文件註解。根據專案規範 R07，公開 API 應包含文件。建議加上說明。

**判斷依據**：diff 中 plugin.rs 第 139 行附近：`pub(crate) struct AppPlugin<R: Runtime>(pub crate::plugin::PluginHandle<R>);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/api/src/app.ts:258</code> 型別 `OnBackButtonPressPayload` 未匯出為公開 API</summary>

型別 `OnBackButtonPressPayload` 在檔案中定義，但未在 export 中列出。雖然在 export 區塊有 `type OnBackButtonPressPayload`，但需確認是否正確匯出。建議檢查並確保公開。

**判斷依據**：diff 中 app.ts 第 255 行附近：`type OnBackButtonPressPayload = {`

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:5</code> 缺少版權和 SPDX 標頭</summary>

新增的 Kotlin 檔案 `AppPlugin.kt` 沒有包含版權和 SPDX 授權標頭。根據專案規範 R01，所有新原始檔應包含。建議加上。

**判斷依據**：diff 中 AppPlugin.kt 開頭沒有版權標頭

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:14</code> 未使用的 import `Invoke` 和 `JSObject`</summary>

檔案中 import 了 `Invoke` 和 `JSObject`，但可能未使用。建議移除未使用的 import 以保持整潔。

**判斷依據**：diff 中 AppPlugin.kt 第 15 行附近

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/plugin/Plugin.kt:149</code> `hasListener` 方法缺少文件註解</summary>

新增的 `hasListener` 方法是公開的，但沒有文件註解。建議加上說明。

**判斷依據**：diff 中 Plugin.kt 第 149 行附近

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:138</code> `register_android_plugin` 的回傳值未處理錯誤</summary>

`register_android_plugin` 可能回傳 `Result`，但程式碼使用 `?` 直接傳播錯誤。這在 `setup` 閉包中可能導致整個初始化失敗，需確認是否為預期行為。

**判斷依據**：diff 中 plugin.rs 第 137 行附近

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 32791 (cache hit 31616) ｜ completion tokens 1980 ｜ PR #6</sub>