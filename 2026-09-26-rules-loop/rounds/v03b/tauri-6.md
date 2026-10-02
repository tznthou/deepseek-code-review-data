<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Android 平台新增返回鍵事件處理，包含 Kotlin 的 AppPlugin、Rust 端的 plugin 註冊、TypeScript API 的 onBackButtonPress 函式，以及相依套件 wry 的版本更新。主要風險在於 AppPlugin 中對 WebView 的強制非空斷言（!!）可能導致 NPE，以及當 JS 端有監聽器時，返回鍵完全交由 JS 處理，若 JS 未呼叫 exit 或 preventDefault，應用程式將無法退出。此外，新增的 Rust 公開結構體 AppPlugin 缺少文件註解，違反專案規範 R07。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32` | WebView 可能為 null 時使用強制非空斷言（!!） | 0.80 |
| ⚠️ | Major | `crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:38` | 有監聽器時返回鍵行為完全由 JS 控制，可能導致應用無法退出 | 0.70 |
| 🔸 | Minor | `crates/tauri/src/app/plugin.rs:148` | [R07] 公開結構體 AppPlugin 缺少文件註解 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32</code> WebView 可能為 null 時使用強制非空斷言（!!）</summary>

在 `handleOnBackPressed` 中，`this@AppPlugin.webView!!.goBack()` 使用了強制非空斷言。雖然 `load(webView)` 通常會在 callback 觸發前被呼叫，但若 WebView 尚未載入或已被釋放，此處會拋出 NullPointerException 導致應用程式崩潰。建議使用安全呼叫或明確檢查 null，例如 `this@AppPlugin.webView?.goBack()`，並在 null 時採取適當的後備行為。

**判斷依據**：diff 中新增的 AppPlugin.kt 第 30 行：`this@AppPlugin.webView!!.goBack()`

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:38</code> 有監聽器時返回鍵行為完全由 JS 控制，可能導致應用無法退出</summary>

當 `hasListener(BACK_BUTTON_EVENT)` 為 true 時，程式僅觸發事件給 JS，不執行任何預設行為（如 goBack 或 finish）。若 JS 端註冊了監聽器但未呼叫 `exit` 或未處理返回鍵，使用者按下返回鍵將沒有任何反應，應用程式無法退出。建議提供明確的 API 讓 JS 端能控制預設行為（例如 preventDefault），或確保 JS 端必須負責退出。

**判斷依據**：diff 中 AppPlugin.kt 第 38-42 行的 else 分支

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/app/plugin.rs:148</code> [R07] 公開結構體 AppPlugin 缺少文件註解</summary>

新增的 `pub(crate) struct AppPlugin<R: Runtime>(pub crate::plugin::PluginHandle<R>);` 是公開 API（雖然是 crate 內部可見），但根據專案規範 R07，所有公開 API 都應包含文件註解。建議為此結構體添加 `///` 文件，說明其用途。

**判斷依據**：diff 中新增的 Rust 結構體定義，無文件註解

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33828 (cache hit 33792) ｜ completion tokens 902 ｜ PR #6</sub>