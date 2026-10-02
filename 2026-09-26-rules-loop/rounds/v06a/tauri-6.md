<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Android 平台新增返回鍵事件處理，包含 Kotlin 插件、Rust 端註冊、前端 API 與權限設定。主要風險在於 Android 插件中 WebView 可能為 null 時使用 `!!` 強制解參考，以及 `onBackPressed` 的遞迴呼叫可能導致 StackOverflow；另有部分新公開 API 缺少文件註解。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | WebView 可能為 null 時使用 `!!` 強制解參考，導致 NPE | 0.90 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35` | `onBackPressed` 遞迴呼叫可能導致 StackOverflow | 0.80 |
| 🔸 | Minor | `packages/api/src/app.ts:267` | [R07] 新公開 API `onBackButtonPress` 缺少文件註解 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> WebView 可能為 null 時使用 `!!` 強制解參考，導致 NPE</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView` 可能尚未被指派（例如 `load()` 尚未被呼叫），但程式碼使用 `this@AppPlugin.webView!!.goBack()` 強制解參考。若 WebView 為 null，將拋出 NullPointerException 並使應用程式崩潰。建議改用安全呼叫 `?.goBack()` 或先檢查 null。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 30 行使用 `!!` 強制解參考，而 `webView` 屬性宣告為 `private var webView: WebView? = null`，且僅在 `load()` 中指派。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35</code> `onBackPressed` 遞迴呼叫可能導致 StackOverflow</summary>

當沒有 listener 且 WebView 無法返回時，程式碼呼叫 `this@AppPlugin.activity.onBackPressed()`。此呼叫會再次觸發 `OnBackPressedCallback`，若條件不變（例如 WebView 仍無法返回），將形成無限遞迴，最終導致 StackOverflowError。建議改用 `activity.finish()` 或先停用 callback 再呼叫。

**判斷依據**：diff 中 AppPlugin.kt 第 33 行呼叫 `onBackPressed()`，而此 callback 已註冊於 `onBackPressedDispatcher`，會再次進入 `handleOnBackPressed`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/api/src/app.ts:267</code> [R07] 新公開 API `onBackButtonPress` 缺少文件註解</summary>

`onBackButtonPress` 是新增的公開 API，但僅有簡短註解，未說明參數、回傳值及使用範例。根據規範 R07，公開 API 應包含完整的文件註解。建議補充詳細說明。

**判斷依據**：diff 中新增的 `onBackButtonPress` 函式僅有 `/** Listens to the backButton event on Android. */` 註解，未符合 R07 的完整文件要求。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33808 (cache hit 31616) ｜ completion tokens 813 ｜ PR #6</sub>