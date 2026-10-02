<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Android 平台新增返回鍵事件處理，包含 Kotlin 插件、Rust 端註冊、前端 API 與權限更新。主要風險在於 Kotlin 插件中的空指標風險、事件監聽器移除後的行為、以及前端 API 未限制平台。建議先修正空指標與監聽器移除問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:31` | webView 可能為 null 導致 NPE | 0.85 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | 監聽器移除後返回鍵行為可能失效 | 0.80 |
| 🔸 | Minor | `packages/api/src/app.ts:267` | onBackButtonPress 未限制平台 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:31</code> webView 可能為 null 導致 NPE</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView?.canGoBack()` 使用了安全呼叫，但下一行 `this@AppPlugin.webView!!.goBack()` 使用了非空斷言。如果 `webView` 尚未初始化（例如在 `load` 被呼叫前觸發返回鍵），會拋出 NullPointerException。建議改用安全呼叫或延遲處理。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 30-31 行，`webView` 為可空屬性，但使用 `!!` 強制解包。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> 監聽器移除後返回鍵行為可能失效</summary>

當 `hasListener(BACK_BUTTON_EVENT)` 為 false 時，程式會停用 callback 並呼叫 `activity.onBackPressed()`，然後重新啟用。但如果前端移除了監聽器，且 webview 無法返回，則會呼叫 `activity.onBackPressed()`，可能導致 Activity 意外關閉。建議在移除監聽器時同步更新 callback 狀態。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 38-40 行，監聽器移除後未處理 callback 狀態。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/api/src/app.ts:267</code> onBackButtonPress 未限制平台</summary>

此 API 僅適用於 Android，但在其他平台呼叫時仍會嘗試註冊監聽器，可能導致錯誤或無效操作。建議在函式內檢查平台或於文件標註。

**判斷依據**：diff 中新增的 app.ts 第 264-266 行，未見平台檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31700 (cache hit 31616) ｜ completion tokens 758 ｜ PR #6</sub>