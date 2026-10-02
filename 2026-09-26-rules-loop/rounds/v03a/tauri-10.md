<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 修正了幾個回歸問題：將 `DeleteCookie` 改回 `SetCookie`、重新命名 `with_window_features` 為 `window_features` 並調整其內部順序、以及將 `on_new_window` 的設定移到桌面平台專屬區塊。主要風險在於 `window_features` 方法中參數順序的變更可能影響行為，且 `on_new_window` 的移動可能導致非桌面平台失去新視窗處理能力。建議確認這些變更的意圖，並補齊對應的變更檔案。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/src/webview/webview_window.rs:1316` | window_features 方法中 size 與 position 的處理順序可能影響視窗建立 | 0.80 |
| ⚠️ | Major | `examples/api/src-tauri/src/lib.rs:74` | on_new_window 設定移至桌面平台區塊可能導致非桌面平台失去新視窗處理 | 0.70 |
| 🔸 | Minor | `crates/tauri/src/webview/mod.rs:22` | 重新匯出 tauri_runtime::Cookie 可能造成 API 混淆 | 0.60 |
| 🔸 | Minor | `crates/tauri/src/webview/webview_window.rs:1317` | inner_size 呼叫中參數間多餘空白 | 0.50 |
| 🔸 | Minor | `crates/tauri/src/webview/webview_window.rs:1321` | position 呼叫中參數間缺少空格 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/src/webview/webview_window.rs:1316</code> window_features 方法中 size 與 position 的處理順序可能影響視窗建立</summary>

在 `window_features` 方法中，原本先處理 `position` 再處理 `size`，現在改為先處理 `size` 再處理 `position`。如果 `NewWindowFeatures` 同時包含 size 和 position，且底層視窗建立邏輯對設定順序敏感（例如某些平台在設定 position 後會重置 size），可能導致最終視窗尺寸或位置不正確。建議確認此順序變更是否為刻意，並驗證在同時指定兩者的情況下行為正確。

**判斷依據**：diff 中顯示原本先處理 position 再處理 size，現在順序對調。

</details>

<details><summary>⚠️ <b>Major</b> — <code>examples/api/src-tauri/src/lib.rs:74</code> on_new_window 設定移至桌面平台區塊可能導致非桌面平台失去新視窗處理</summary>

原本 `on_new_window` 的設定在所有平台都會執行，現在被移入 `#[cfg(all(desktop, not(test)))]` 區塊。這表示在非桌面平台（例如行動裝置）上，當 WebView 請求開啟新視窗時，將不會有自訂的處理邏輯，可能導致新視窗無法建立或行為不符合預期。請確認此變更是否為刻意，並考慮是否需要在其他平台提供替代處理。

**判斷依據**：diff 顯示 on_new_window 的設定從原本的全平台區塊移入 cfg(all(desktop, not(test))) 區塊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/mod.rs:22</code> 重新匯出 tauri_runtime::Cookie 可能造成 API 混淆</summary>

新增 `pub use tauri_runtime::Cookie;` 並加上註解「Remove this re-export in v3」。這可能是為了向後相容，但同時存在原本的 `cookie` crate 匯出，可能導致使用者混淆。建議確認此匯出是否必要，並考慮在文件或 deprecation 標記中說明。

**判斷依據**：diff 中新增了此匯出。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/webview_window.rs:1317</code> inner_size 呼叫中參數間多餘空白</summary>

`self.window_builder.inner_size(size.width,    size.height);` 中 `size.width,` 和 `size.height` 之間有多餘的空白，不符合 rustfmt 規範（R03）。建議執行 `cargo fmt` 修正。

**判斷依據**：diff 中該行有多餘空白。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/webview_window.rs:1321</code> position 呼叫中參數間缺少空格</summary>

`self.window_builder.position(position.x,position.y);` 中 `position.x,` 和 `position.y` 之間缺少空格，不符合 rustfmt 規範（R03）。建議執行 `cargo fmt` 修正。

**判斷依據**：diff 中該行缺少空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5518 (cache hit 3328) ｜ completion tokens 1341 ｜ PR #10</sub>