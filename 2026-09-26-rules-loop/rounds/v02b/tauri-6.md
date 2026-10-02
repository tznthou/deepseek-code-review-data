<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 Android 返回鍵事件處理，包含 Kotlin 的 AppPlugin、Rust 端 plugin 註冊、JS API 的 onBackButtonPress，以及對應的 change files 與權限更新。主要風險在於 AppPlugin 中對 WebView 的強制非空斷言（!!）可能導致 NPE、OnBackPressedCallback 的啟用狀態管理可能造成返回鍵失效，以及缺少對應的測試。整體功能方向合理，但需修正上述問題以確保穩定性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | 強制非空斷言可能導致 NPE | 0.90 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | OnBackPressedCallback 啟用狀態管理可能導致返回鍵失效 | 0.80 |
| 🔸 | Minor | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:29` | 缺少對應的單元測試 | 0.70 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:138` | Android plugin 註冊缺少錯誤處理 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> 強制非空斷言可能導致 NPE</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView!!.goBack()` 使用了強制非空斷言。如果 `webView` 尚未初始化（例如 `load` 未被呼叫），按下返回鍵會拋出 NullPointerException 並導致應用程式崩潰。建議改用安全呼叫（`?.goBack()`）或加入 null 檢查。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 31 行使用 `!!` 操作符，而 `webView` 是 nullable 且僅在 `load` 中賦值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> OnBackPressedCallback 啟用狀態管理可能導致返回鍵失效</summary>

在 `handleOnBackPressed` 中，當沒有 listener 且 webView 無法返回時，會先將 `this.isEnabled = false`，呼叫 `activity.onBackPressed()`，再設回 `true`。如果 `activity.onBackPressed()` 內部觸發了非同步操作或拋出例外，`isEnabled` 可能永遠保持 false，導致後續返回鍵無效。建議使用 try-finally 確保狀態恢復，或改用其他方式處理預設行為。

**判斷依據**：diff 中 AppPlugin.kt 第 33-35 行，狀態切換與呼叫之間沒有例外保護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:29</code> 缺少對應的單元測試</summary>

新增的返回鍵處理邏輯（包含 listener 分支與 webView 返回分支）沒有對應的測試。建議為 `AppPlugin` 的 `handleOnBackPressed` 行為撰寫單元測試，涵蓋有/無 listener、webView 可/不可返回等情境。

**判斷依據**：diff 中新增的 AppPlugin.kt 沒有包含任何測試程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:138</code> Android plugin 註冊缺少錯誤處理</summary>

`register_android_plugin` 回傳 `Result`，但此處使用 `?` 直接傳播錯誤。若註冊失敗，整個 plugin 初始化會失敗，可能導致應用程式無法啟動。建議考慮記錄錯誤並提供 fallback 或更明確的錯誤訊息。

**判斷依據**：diff 中 plugin.rs 第 136 行使用 `?` 傳播錯誤，未見任何錯誤處理或日誌。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33818 (cache hit 33792) ｜ completion tokens 1007 ｜ PR #6</sub>