<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Android 加入返回鍵事件處理，包含新增 AppPlugin、調整 TauriActivity 與權限設定，並更新相依套件。主要風險在於 AppPlugin 的返回鍵處理邏輯：當沒有 JS listener 時，直接呼叫 activity.onBackPressed() 可能造成遞迴或非預期行為；此外，webView 可能為 null 時使用 !! 強制解參考有潛在 NPE 風險。建議先修正這些正確性問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35` | 返回鍵處理可能造成遞迴或非預期行為 | 0.90 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | webView 可能為 null 時使用 !! 強制解參考 | 0.80 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:51` | exit 命令未處理 activity 可能為 null 的情況 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35</code> 返回鍵處理可能造成遞迴或非預期行為</summary>

當沒有 JS listener 且 webView 無法返回時，程式碼呼叫 `this@AppPlugin.activity.onBackPressed()`。但此 callback 已註冊在 `onBackPressedDispatcher` 上，而 `activity.onBackPressed()` 通常會再次觸發 dispatcher，導致此 callback 被重複呼叫，可能造成無窮遞迴或非預期行為。

建議改為直接呼叫 `activity.finish()` 或使用 `onBackPressedDispatcher.onBackPressed()` 以外的機制來結束 activity。

**判斷依據**：在 `handleOnBackPressed` 中，當 `!hasListener(BACK_BUTTON_EVENT)` 且 `webView?.canGoBack() != true` 時，執行 `this@AppPlugin.activity.onBackPressed()`。由於此 callback 已透過 `onBackPressedDispatcher.addCallback` 註冊，呼叫 `activity.onBackPressed()` 會再次觸發 dispatcher，可能導致遞迴。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> webView 可能為 null 時使用 !! 強制解參考</summary>

在 `handleOnBackPressed` 中，當 `webView?.canGoBack() == true` 時，使用 `this@AppPlugin.webView!!.goBack()`。雖然 `load` 方法會在 WebView 載入時設定 `webView`，但若 callback 在 `load` 之前被觸發（例如 activity 初始化期間），`webView` 可能仍為 null，導致 NPE。

建議使用安全呼叫或明確檢查 null。

**判斷依據**：`webView` 宣告為 `private var webView: WebView? = null`，並在 `load` 中賦值。在 `handleOnBackPressed` 中，條件 `this@AppPlugin.webView?.canGoBack() == true` 確保 `webView` 非 null，但使用 `!!` 仍可能因時序問題（如 callback 在 `load` 前觸發）而拋出 NPE。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:51</code> exit 命令未處理 activity 可能為 null 的情況</summary>

`exit` 命令直接呼叫 `activity.finish()`。若 activity 已銷毀或為 null，可能拋出 NPE。雖然在正常情況下 activity 不應為 null，但建議加入防禦性檢查。

**判斷依據**：`activity` 在建構子中傳入，但未檢查是否為 null。若在 activity 銷毀後呼叫此命令，可能導致 NPE。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31736 (cache hit 31616) ｜ completion tokens 944 ｜ PR #6</sub>