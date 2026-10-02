<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Android 加入返回鍵事件處理，新增 AppPlugin 與前端 API。主要風險在於 AppPlugin 的返回鍵處理邏輯：當沒有 JS listener 時，會直接呼叫 activity.onBackPressed()，可能造成非預期的 Activity 關閉或與其他 callback 衝突；此外，將 webView 設為可空並使用 !! 強制解包，若 load 未被呼叫可能導致 NPE。建議先修正返回鍵的預設行為與空值處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | 無 listener 時直接呼叫 onBackPressed 可能導致非預期關閉 | 0.80 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | webView 可空但使用強制解包，可能 NPE | 0.70 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46` | 強制轉型為 AppCompatActivity 可能導致 ClassCastException | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> 無 listener 時直接呼叫 onBackPressed 可能導致非預期關閉</summary>

當沒有 JS listener 且 webView 無法返回時，程式碼會呼叫 `activity.onBackPressed()`。這會觸發 Activity 的預設返回行為，通常是關閉 Activity。若開發者希望攔截返回鍵但尚未註冊 listener，或 listener 被移除的瞬間，可能導致應用意外退出。建議改為停用 callback 並讓系統處理，或提供明確的預設行為。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 31-33 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> webView 可空但使用強制解包，可能 NPE</summary>

`webView` 宣告為 `WebView?`，但在 `handleOnBackPressed` 中使用 `this@AppPlugin.webView!!.goBack()`。若 `load` 尚未被呼叫（例如 plugin 初始化順序問題），`webView` 為 null，會導致 NullPointerException。建議使用安全呼叫或延遲初始化。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 27 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46</code> 強制轉型為 AppCompatActivity 可能導致 ClassCastException</summary>

在建構子中直接 `(activity as AppCompatActivity)`，若傳入的 Activity 不是 AppCompatActivity（例如使用非 AppCompat 主題），會拋出 ClassCastException。建議檢查型別或改用 ComponentActivity。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 15 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33626 (cache hit 1536) ｜ completion tokens 745 ｜ PR #6</sub>