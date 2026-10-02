<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 Android 平台新增返回鍵事件處理，包含 Kotlin 插件、Rust 端註冊、前端 API 與權限設定。主要風險在於 Kotlin 插件中 `OnBackPressedCallback` 的啟用狀態管理可能導致返回鍵失效，以及 `webView` 可能為 null 時使用 `!!` 強制解參考。此外，`AppPlugin` 的 `exit` 指令未處理 `activity.finish()` 後的流程，且缺少對應測試。整體而言，功能方向正確，但需修正上述問題以確保穩定性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34` | 返回鍵處理邏輯可能導致返回鍵永久失效 | 0.90 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | `webView` 可能為 null 時使用 `!!` 強制解參考 | 0.80 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:51` | `exit` 指令未處理 `activity.finish()` 後的流程 | 0.70 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:138` | Android 插件註冊使用 `?` 可能導致初始化失敗 | 0.60 |
| 🔸 | Minor | `packages/api/src/app.ts:267` | 新增的 `onBackButtonPress` 函式缺少文件範例 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34</code> 返回鍵處理邏輯可能導致返回鍵永久失效</summary>

在 `handleOnBackPressed` 中，當沒有監聽器且 `webView` 無法返回時，程式碼會將 `this.isEnabled = false`，然後呼叫 `activity.onBackPressed()`，最後再將 `this.isEnabled = true`。然而，`activity.onBackPressed()` 可能觸發 Activity 的銷毀或狀態改變，導致後續的 `this.isEnabled = true` 無法執行，或 callback 已被移除，造成返回鍵永久失效。建議改用 `OnBackPressedCallback` 的 `isEnabled` 屬性動態控制，或避免直接呼叫 `activity.onBackPressed()`，改以其他方式結束 Activity。

**判斷依據**：diff 中新增的 `AppPlugin.kt` 第 30-32 行顯示此邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> `webView` 可能為 null 時使用 `!!` 強制解參考</summary>

在 `handleOnBackPressed` 中，當 `webView` 尚未初始化（例如 `load` 未被呼叫）時，`this@AppPlugin.webView!!.goBack()` 會拋出 `NullPointerException`。雖然 `canGoBack()` 檢查了 null，但後續的 `!!` 仍不安全。建議使用安全呼叫或明確處理 null 情況。

**判斷依據**：diff 中新增的 `AppPlugin.kt` 第 27 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:51</code> `exit` 指令未處理 `activity.finish()` 後的流程</summary>

`exit` 指令呼叫 `activity.finish()` 後立即 `invoke.resolve()`，但未考慮 Activity 可能尚未完全銷毀，或需要等待其他清理工作。此外，若 `finish()` 觸發 onDestroy，後續的 `resolve` 可能無法正確傳遞。建議確認此行為是否符合預期，或考慮延遲 resolve。

**判斷依據**：diff 中新增的 `AppPlugin.kt` 第 48-49 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:138</code> Android 插件註冊使用 `?` 可能導致初始化失敗</summary>

在 `setup` 閉包中，`register_android_plugin` 回傳 `Result`，使用 `?` 會將錯誤向上傳播，可能導致整個應用初始化失敗。若插件註冊失敗應視為致命錯誤，則此寫法合理；否則應考慮記錄錯誤並繼續。

**判斷依據**：diff 中 `crates/tauri/src/app/plugin.rs` 第 135 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/api/src/app.ts:267</code> 新增的 `onBackButtonPress` 函式缺少文件範例</summary>

根據專案規範 R07，公開 API 應包含文件註解。此函式雖有簡短說明，但缺少使用範例，可能降低開發者體驗。建議補充範例程式碼。

**判斷依據**：diff 中 `packages/api/src/app.ts` 第 255-257 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33828 (cache hit 31616) ｜ completion tokens 1263 ｜ PR #6</sub>