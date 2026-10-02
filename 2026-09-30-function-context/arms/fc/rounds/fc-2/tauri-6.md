<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 Android 返回鍵事件支援，包含 Kotlin 端的 AppPlugin、Rust 端的 plugin 註冊、以及 JS API 的 onBackButtonPress。主要風險在於 Kotlin 端對 WebView 的 null 處理與 Activity 型別假設，可能導致特定情境下的當機；此外，事件觸發後未提供 preventDefault 機制，可能限制前端控制權。整體方向正確，但建議先處理 Kotlin 端的穩定性問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | webView 可能為 null 時使用 !! 強制解參考，可能導致 NullPointerException | 0.80 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46` | 強制轉型 activity 為 AppCompatActivity 可能導致 ClassCastException | 0.70 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:42` | 事件觸發後未提供 preventDefault 機制，前端無法阻止預設行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> webView 可能為 null 時使用 !! 強制解參考，可能導致 NullPointerException</summary>

在 `handleOnBackPressed` 中，當 `hasListener(BACK_BUTTON_EVENT)` 為 false 且 `webView?.canGoBack()` 不為 true 時，會執行 `this@AppPlugin.webView!!.goBack()`。但 `webView` 屬性在 `load(webView: WebView)` 被呼叫前為 null，若返回鍵在 WebView 載入前被觸發，則會拋出 NullPointerException。建議改用安全呼叫或延遲處理。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 31 行：`this@AppPlugin.webView!!.goBack()`，而 `webView` 為 nullable 且僅在 `load` 中賦值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46</code> 強制轉型 activity 為 AppCompatActivity 可能導致 ClassCastException</summary>

在建構子中直接將 `activity` 轉型為 `AppCompatActivity`，但 Tauri 可能支援其他 Activity 型別（如 ComponentActivity），若傳入非 AppCompatActivity 的實例，將在初始化時拋出 ClassCastException。建議檢查型別或改用 ComponentActivity 的 `onBackPressedDispatcher`。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 40 行：`(activity as AppCompatActivity).onBackPressedDispatcher.addCallback(activity, callback)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:42</code> 事件觸發後未提供 preventDefault 機制，前端無法阻止預設行為</summary>

當有 listener 時，僅觸發事件並傳遞 `canGoBack` 資訊，但未提供類似 `preventDefault` 的機制讓前端阻止預設的返回行為（例如關閉頁面或退出應用）。這可能限制前端對返回鍵的完全控制。建議參考其他 Tauri 事件（如 `onCloseRequested`）提供可選的 preventDefault 功能。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 35 行：`trigger(BACK_BUTTON_EVENT, data)`，且無任何 preventDefault 相關邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33626 (cache hit 33536) ｜ completion tokens 870 ｜ PR #6</sub>