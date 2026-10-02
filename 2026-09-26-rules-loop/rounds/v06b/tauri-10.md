<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了先前 PR 引入的幾個回歸問題：將 `DeleteCookie` 改回 `SetCookie`、將 `with_window_features` 更名為 `window_features` 並調整其內部邏輯順序、將 `on_new_window` 回呼移至桌面平台專屬區塊，並移除了不必要的 `use` 陳述式。主要風險在於 `window_features` 方法中參數順序的變更可能造成行為差異，以及 `on_new_window` 的移動可能影響非桌面平台的行為。建議先確認這些變更的意圖與影響範圍。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri/src/webview/webview_window.rs:1315` | window_features 方法中 size 與 position 的設定順序變更可能影響視窗建立行為 | 0.80 |
| 🔸 | Minor | `crates/tauri/src/webview/webview_window.rs:1317` | [R03] 程式碼格式不符合 rustfmt 規範 | 0.90 |
| 🔸 | Minor | `crates/tauri/src/webview/webview_window.rs:1321` | [R03] 程式碼格式不符合 rustfmt 規範 | 0.90 |
| 🔸 | Minor | `examples/api/src-tauri/src/lib.rs:74` | on_new_window 回呼移至桌面平台專屬區塊可能影響非桌面平台行為 | 0.70 |
| 🔸 | Minor | `crates/tauri/src/webview/mod.rs:22` | 重新匯出 tauri_runtime::Cookie 可能造成 API 混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri/src/webview/webview_window.rs:1315</code> window_features 方法中 size 與 position 的設定順序變更可能影響視窗建立行為</summary>

原本的 `with_window_features` 先設定 position，再設定 size；新的 `window_features` 則先設定 size，再設定 position。雖然在大多數情況下順序不影響最終結果，但若 `window_builder` 的 `position` 或 `inner_size` 方法有相依性（例如某些平台會根據 position 調整 size），則可能造成行為差異。建議確認此變更是否為刻意為之，並考慮保持原有順序以降低風險。

**判斷依據**：diff 顯示原本先處理 position，後處理 size；新程式碼則相反。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/webview_window.rs:1317</code> [R03] 程式碼格式不符合 rustfmt 規範</summary>

`inner_size(size.width,    size.height)` 中有多餘的空格，且 `position(position.x,position.y)` 缺少逗號後的空格。這會導致 `cargo fmt --check` 失敗。建議執行 `cargo fmt` 修正。

**判斷依據**：diff 中該行有明顯的格式問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/webview_window.rs:1321</code> [R03] 程式碼格式不符合 rustfmt 規範</summary>

`position(position.x,position.y)` 缺少逗號後的空格，應為 `position(position.x, position.y)`。建議執行 `cargo fmt` 修正。

**判斷依據**：diff 中該行有明顯的格式問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>examples/api/src-tauri/src/lib.rs:74</code> on_new_window 回呼移至桌面平台專屬區塊可能影響非桌面平台行為</summary>

原本 `on_new_window` 回呼在所有平台上都會被設定，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內。這表示在非桌面平台（如行動裝置）上，新視窗請求將不再被處理，可能導致功能回歸。若此變更為刻意，建議在 PR 描述中說明原因；否則應考慮保留跨平台行為。

**判斷依據**：diff 顯示 `on_new_window` 設定被移入 `#[cfg(all(desktop, not(test)))]` 區塊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/mod.rs:22</code> 重新匯出 tauri_runtime::Cookie 可能造成 API 混淆</summary>

新增 `pub use tauri_runtime::Cookie;` 並加上註解「Remove this re-export in v3」。這可能是為了向後相容，但同時存在原本的 `cookie` crate 匯出，可能造成名稱衝突或混淆。建議確認此匯出是否必要，並考慮使用更明確的名稱或文件說明。

**判斷依據**：diff 顯示新增了此匯出。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5498 (cache hit 5376) ｜ completion tokens 1346 ｜ PR #10</sub>