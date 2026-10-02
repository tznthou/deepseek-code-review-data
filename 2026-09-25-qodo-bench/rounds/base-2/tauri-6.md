<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Android 平台新增返回鍵事件處理，包含 Kotlin 端的 AppPlugin、Rust 端的 plugin 註冊、以及 JS API 的 onBackButtonPress。主要風險在於 Kotlin 端對 WebView 的強制非空斷言（!!）可能導致 NPE，以及當 JS 端有監聽器時，返回鍵完全由前端決定，若前端未處理可能造成應用無法退出。另外，權限設定新增了 register_listener 與 remove_listener，但未看到對應的測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | WebView 可能為 null 時使用 !! 導致 NPE | 0.80 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | 當有監聽器時，返回鍵行為完全由前端控制，可能導致應用無法退出 | 0.75 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46` | 強制轉型為 AppCompatActivity 可能導致 ClassCastException | 0.60 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:148` | AppPlugin 結構體未使用可能導致 dead_code 警告 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> WebView 可能為 null 時使用 !! 導致 NPE</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView!!.goBack()` 使用了非空斷言。雖然 `load` 方法通常會在 WebView 建立後被呼叫，但若返回鍵在 `load` 之前觸發，或 WebView 因某種原因被設為 null，則會拋出 NullPointerException。建議改用安全呼叫或檢查 null。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 29 行使用了 `!!`，而 `webView` 屬性宣告為 `private var webView: WebView? = null`，可能尚未初始化。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> 當有監聽器時，返回鍵行為完全由前端控制，可能導致應用無法退出</summary>

當 `hasListener(BACK_BUTTON_EVENT)` 為 true 時，程式只觸發事件給前端，不執行任何預設行為（如返回上一頁或退出）。如果前端註冊了監聽器但未在處理函式中呼叫退出或導航，使用者按下返回鍵將沒有任何反應，可能造成應用卡死。建議提供一個方法讓前端可以明確要求執行預設行為，或在文件中清楚說明。

**判斷依據**：diff 中 AppPlugin.kt 第 34-38 行，當有 listener 時只 trigger 事件，沒有 fallback 行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46</code> 強制轉型為 AppCompatActivity 可能導致 ClassCastException</summary>

在建構子中 `(activity as AppCompatActivity)` 直接轉型，如果傳入的 Activity 不是 AppCompatActivity（例如使用非 AppCompat 主題），會拋出 ClassCastException。雖然 Tauri 通常使用 AppCompatActivity，但建議使用更安全的方式取得 OnBackPressedDispatcher，例如使用 `activity.onBackPressedDispatcher`（需要 androidx.activity 擴展）。

**判斷依據**：diff 中 AppPlugin.kt 第 42 行直接轉型。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:148</code> AppPlugin 結構體未使用可能導致 dead_code 警告</summary>

新增的 `AppPlugin` 結構體僅在 Android 上使用，但未看到實際使用的地方（可能在其他檔案中）。如果未使用，Rust 編譯器會發出 dead_code 警告。建議確認是否有使用，或加上 `#[allow(dead_code)]`。

**判斷依據**：diff 中新增的結構體，但未見使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31736 (cache hit 31616) ｜ completion tokens 1068 ｜ PR #6</sub>