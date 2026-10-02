<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Android 新增返回鍵事件處理，包含 Kotlin 外掛、Rust 端註冊、前端 API 與權限更新。主要風險在於 Kotlin 外掛中的返回鍵處理邏輯：當 WebView 無法回上一頁時，會暫時停用 callback 並呼叫 activity.onBackPressed()，但若 activity 非 AppCompatActivity 或 onBackPressed 未正確觸發，可能導致 callback 永久停用或行為不一致。此外，前端 API 的 onBackButtonPress 未限制平台，在非 Android 環境呼叫可能產生未預期的行為。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | 返回鍵處理可能導致 callback 永久停用 | 0.90 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46` | 強制轉型為 AppCompatActivity 可能導致 ClassCastException | 0.80 |
| ⚠️ | Major | `packages/api/src/app.ts:267` | onBackButtonPress 未限制平台，非 Android 呼叫可能無效 | 0.70 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | webView 可能為 null 時使用 !! 強制解參考 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> 返回鍵處理可能導致 callback 永久停用</summary>

在 `handleOnBackPressed` 中，當 WebView 無法回上一頁時，程式碼會先將 `this.isEnabled = false`，然後呼叫 `activity.onBackPressed()`，最後再將 `this.isEnabled = true`。然而，如果 `activity.onBackPressed()` 拋出例外或未正常返回（例如 activity 不是 `AppCompatActivity` 或系統行為不同），`isEnabled` 將永遠保持 `false`，導致後續返回鍵事件完全失效。建議使用 try-finally 確保 `isEnabled` 恢復，或改用 `OnBackPressedCallback` 的 `setEnabled` 方法管理狀態。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 31-33 行顯示了此邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46</code> 強制轉型為 AppCompatActivity 可能導致 ClassCastException</summary>

`(activity as AppCompatActivity)` 假設傳入的 activity 一定是 `AppCompatActivity`。如果 Tauri 支援的 activity 類型未來擴展或使用者自訂 activity 未繼承 `AppCompatActivity`，此處將拋出 `ClassCastException`。建議檢查 activity 類型或使用更通用的 `ComponentActivity`（`OnBackPressedDispatcher` 的擁有者）。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 37 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/api/src/app.ts:267</code> onBackButtonPress 未限制平台，非 Android 呼叫可能無效</summary>

`onBackButtonPress` 函式直接呼叫 `addPluginListener`，但此功能僅在 Android 上實作。在 iOS 或桌面平台呼叫此函式時，可能導致錯誤或未預期的行為。建議在函式內檢查平台（例如使用 `isTauri()` 或平台偵測）並在非 Android 平台拋出明確錯誤或直接 no-op。

**判斷依據**：diff 中新增的 app.ts 第 262-270 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> webView 可能為 null 時使用 !! 強制解參考</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView!!.goBack()` 使用了非空斷言。雖然 `load` 方法應該在 callback 觸發前被呼叫，但若時序異常（例如 callback 在 `load` 前觸發），將導致 `NullPointerException`。建議使用安全呼叫或檢查 null。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 25 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31700 (cache hit 1408) ｜ completion tokens 1126 ｜ PR #6</sub>