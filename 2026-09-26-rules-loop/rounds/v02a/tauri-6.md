<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Android 新增返回鍵事件處理，包含 Kotlin 外掛、Rust 端註冊、JS API 與權限更新。主要風險在於 Kotlin 外掛的返回鍵處理邏輯：當沒有監聽器時，會直接呼叫 activity.onBackPressed()，可能導致非預期的 Activity 關閉；此外，外掛初始化時強制轉型為 AppCompatActivity，若宿主 Activity 非此類型會拋出 ClassCastException。另有 webView 可空性處理不一致、缺少測試等問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | 無監聽器時直接呼叫 onBackPressed 可能導致非預期關閉 | 0.90 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46` | 強制轉型為 AppCompatActivity 可能導致 ClassCastException | 0.85 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:31` | webView 可空性處理不一致 | 0.80 |
| ⚠️ | Major | `crates/tauri/src/app/plugin.rs:138` | 缺少對 Android 外掛註冊的錯誤處理 | 0.75 |
| 🔸 | Minor | `packages/api/src/app.ts:267` | 缺少對 onBackButtonPress 的測試 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> 無監聽器時直接呼叫 onBackPressed 可能導致非預期關閉</summary>

在 `handleOnBackPressed` 中，當沒有監聽器且 webView 無法返回時，程式碼會停用 callback、呼叫 `activity.onBackPressed()`，然後重新啟用 callback。然而，`onBackPressed()` 的預設行為是結束 Activity，這會導致應用程式直接關閉，而不是讓系統處理返回事件。這可能不是預期的行為，特別是在 Tauri 應用程式中，返回鍵通常應該由前端處理。建議改為觸發一個事件或讓系統處理，而不是直接呼叫 `onBackPressed()`。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 34-36 行顯示了這個邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46</code> 強制轉型為 AppCompatActivity 可能導致 ClassCastException</summary>

在 `init` 區塊中，`(activity as AppCompatActivity)` 假設宿主 Activity 一定是 AppCompatActivity。如果 Tauri 應用程式使用其他類型的 Activity（例如 ComponentActivity），這將拋出 ClassCastException。建議使用 `activity as? AppCompatActivity` 並處理 null 的情況，或改用 `OnBackPressedDispatcher` 而不依賴 AppCompatActivity。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 40 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:31</code> webView 可空性處理不一致</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView?.canGoBack()` 使用了安全呼叫，但下一行 `this@AppPlugin.webView!!.goBack()` 使用了非空斷言。如果 `webView` 為 null，這將導致 NullPointerException。雖然 `load` 方法應該在之前被呼叫，但沒有保證。建議使用安全呼叫或明確處理 null 情況。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 28-29 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/src/app/plugin.rs:138</code> 缺少對 Android 外掛註冊的錯誤處理</summary>

在 `setup` 閉包中，`_api.register_android_plugin("app.tauri", "AppPlugin")?` 使用了 `?` 運算子，如果註冊失敗，整個 setup 會失敗並可能導致應用程式無法啟動。但沒有提供任何錯誤訊息或回退機制。建議記錄錯誤或提供更詳細的錯誤處理。

**判斷依據**：diff 中新增的 plugin.rs 第 145 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/api/src/app.ts:267</code> 缺少對 onBackButtonPress 的測試</summary>

新增的 `onBackButtonPress` 函數沒有對應的測試。考慮到這是新的公開 API，建議添加單元測試以驗證其行為，特別是在不同平台上的表現。

**判斷依據**：diff 中新增的 app.ts 第 266-268 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33818 (cache hit 1536) ｜ completion tokens 1235 ｜ PR #6</sub>