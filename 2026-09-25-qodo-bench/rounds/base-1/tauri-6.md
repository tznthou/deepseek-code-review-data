<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Android 平台新增返回鍵事件處理，包含 Kotlin 的 AppPlugin、Rust 端的 plugin 註冊、以及 JS API 的 onBackButtonPress。主要風險在於 AppPlugin 的返回鍵處理邏輯：當沒有 JS listener 時，若 WebView 無法回上一頁，會直接呼叫 activity.onBackPressed()，可能導致 Activity 意外關閉；此外，callback 的啟用狀態管理與 WebView 的 null 處理也有潛在問題。建議先修正這些邏輯再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | 無 listener 且 WebView 無法回上一頁時，直接呼叫 activity.onBackPressed() 可能導致 Activity 意外關閉 | 0.90 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | callback 的 isEnabled 狀態管理可能導致返回鍵失效 | 0.80 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | webView 可能為 null 時使用 !! 強制解包，存在 NPE 風險 | 0.70 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:42` | trigger 事件時未處理 listener 可能為空的情況 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> 無 listener 且 WebView 無法回上一頁時，直接呼叫 activity.onBackPressed() 可能導致 Activity 意外關閉</summary>

在 `handleOnBackPressed` 中，當 `!hasListener(BACK_BUTTON_EVENT)` 且 `webView?.canGoBack() != true` 時，會執行 `this@AppPlugin.activity.onBackPressed()`。這會觸發 Activity 的預設返回行為，通常是關閉 Activity。如果開發者沒有註冊 listener，使用者按下返回鍵就會直接退出應用程式，這可能不是預期的行為（例如應用程式想要攔截返回鍵但尚未設定 listener）。建議改為不執行任何動作，或提供明確的 API 讓開發者控制是否退出。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 30-32 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> callback 的 isEnabled 狀態管理可能導致返回鍵失效</summary>

在 `handleOnBackPressed` 中，當沒有 listener 且 WebView 無法回上一頁時，會先將 `this.isEnabled = false`，然後呼叫 `activity.onBackPressed()`，最後再設回 `true`。然而，`activity.onBackPressed()` 可能會觸發 Activity 的銷毀或暫停，此時 callback 可能已被移除，重新設為 `true` 可能無效或造成記憶體洩漏。此外，如果 `activity.onBackPressed()` 拋出例外，`isEnabled` 將永遠保持 `false`，導致後續返回鍵完全失效。建議使用 try-finally 確保狀態恢復，或避免直接呼叫 `onBackPressed()`。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 30-32 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> webView 可能為 null 時使用 !! 強制解包，存在 NPE 風險</summary>

在 `handleOnBackPressed` 中，當 `webView?.canGoBack() == true` 時，使用 `this@AppPlugin.webView!!.goBack()`。雖然 `load` 方法應該在 callback 觸發前被呼叫，但若 WebView 尚未載入或已被銷毀，`webView` 可能為 null，導致 NullPointerException。建議使用安全呼叫或明確檢查 null。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 27 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:42</code> trigger 事件時未處理 listener 可能為空的情況</summary>

在 `handleOnBackPressed` 的 else 分支中，直接呼叫 `trigger(BACK_BUTTON_EVENT, data)`。如果 `hasListener` 回傳 true 但實際上 listener 已被移除（例如非同步操作），`trigger` 可能不會有任何效果，但這可能不是問題。然而，如果 listener 在觸發前被移除，事件將丟失，開發者可能無法得知。建議在觸發前再次檢查 listener 是否存在。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 38 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31736 (cache hit 1536) ｜ completion tokens 1176 ｜ PR #6</sub>