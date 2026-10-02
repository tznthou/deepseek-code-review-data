<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了先前 PR 引入的幾個回歸問題：將 `DeleteCookie` 改回 `SetCookie`、將 `with_window_features` 更名為 `window_features` 並調整其內部順序、以及將 `on_new_window` 回呼的註冊移至桌面平台專屬區塊。主要風險在於 `window_features` 方法中參數順序的變更可能影響行為，且 `on_new_window` 的移動可能導致非桌面平台失去新視窗處理能力。此外，缺少變更檔案（change file）可能違反專案規範。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/src/webview/webview_window.rs:1316` | window_features 方法中 size 與 position 的處理順序變更可能影響視窗建立行為 | 0.80 |
| ⚠️ | Major | `examples/api/src-tauri/src/lib.rs:76` | on_new_window 回呼移至桌面平台專屬區塊可能導致非桌面平台失去新視窗處理 | 0.70 |
| 🔸 | Minor | `crates/tauri/src/webview/mod.rs:22` | 重新匯出 tauri_runtime::Cookie 可能造成 API 混淆 | 0.60 |
| 🔸 | Minor | `crates/tauri/src/webview/webview_window.rs:1317` | 程式碼格式問題：inner_size 呼叫中參數間多餘空白 | 0.50 |
| 🔸 | Minor | `crates/tauri/src/webview/webview_window.rs:1321` | 程式碼格式問題：position 呼叫中缺少逗號後空格 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/src/webview/webview_window.rs:1316</code> window_features 方法中 size 與 position 的處理順序變更可能影響視窗建立行為</summary>

在 `window_features` 方法中，原本先處理 `position` 再處理 `size`，現在改為先處理 `size` 再處理 `position`。雖然在大多數情況下順序不影響最終結果，但若 `position` 或 `size` 的設定有相依性（例如某些平台在設定位置後會重置大小），可能導致行為不一致。建議確認此變更的必要性，或恢復原本順序以降低風險。

**判斷依據**：diff 中顯示原本先處理 position 再處理 size，現在順序對調。

</details>

<details><summary>⚠️ <b>Major</b> — <code>examples/api/src-tauri/src/lib.rs:76</code> on_new_window 回呼移至桌面平台專屬區塊可能導致非桌面平台失去新視窗處理</summary>

原本 `on_new_window` 回呼在所有平台都會註冊，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內。這表示在非桌面平台（例如行動裝置）上，當 WebView 要求開啟新視窗時，將不會有自訂處理邏輯，可能導致新視窗無法建立或行為不一致。若此回呼僅適用於桌面平台，則應在文件或註解中說明；否則應考慮保留在所有平台。

**判斷依據**：diff 顯示 `on_new_window` 的註冊從原本的全平台區塊移至 `#[cfg(all(desktop, not(test)))]` 區塊內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/mod.rs:22</code> 重新匯出 tauri_runtime::Cookie 可能造成 API 混淆</summary>

新增 `pub use tauri_runtime::Cookie;` 並加上註解「Remove this re-export in v3」。這可能是為了向後相容，但同時存在 `cookie::Cookie` 的引用被移除，可能導致下游使用者混淆應使用哪個 Cookie 型別。建議在文件或遷移指南中清楚說明。

**判斷依據**：diff 中新增了此重新匯出，並移除了原本的 `use cookie::Cookie;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/webview_window.rs:1317</code> 程式碼格式問題：inner_size 呼叫中參數間多餘空白</summary>

在 `inner_size(size.width,    size.height)` 中，`size.width` 與 `size.height` 之間有四個空格，不符合一般格式慣例。雖然不影響功能，但可能違反 rustfmt 規範（R03）。

**判斷依據**：diff 中該行顯示多餘空白。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/webview_window.rs:1321</code> 程式碼格式問題：position 呼叫中缺少逗號後空格</summary>

在 `position(position.x,position.y)` 中，逗號後缺少空格，不符合一般格式慣例。可能違反 rustfmt 規範（R03）。

**判斷依據**：diff 中該行顯示缺少空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5508 (cache hit 3328) ｜ completion tokens 1344 ｜ PR #10</sub>