<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 修正了先前 PR 引入的幾個回歸：將 `DeleteCookie` 改回 `SetCookie`、把 `with_window_features` 改名為 `window_features` 並調整其內部順序、將 `on_new_window` 的設定移到桌面平台專屬區塊。主要風險在於 `window_features` 方法中 `inner_size` 呼叫的參數格式錯誤（多餘空格），可能導致編譯失敗；另外 `SetCookie` 的語意與方法名稱不一致，需確認是否為預期行為。整體而言，改動方向合理，但需修正格式問題並確認 cookie 處理邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri/src/webview/webview_window.rs:1317` | [R03] `inner_size` 呼叫參數格式錯誤，可能導致編譯失敗 | 0.95 |
| ⚠️ | Major | `crates/tauri-runtime-wry/src/lib.rs:1718` | `SetCookie` 訊息與方法名稱不一致，可能導致 cookie 刪除失敗 | 0.80 |
| 🔸 | Minor | `crates/tauri/src/webview/webview_window.rs:1321` | [R03] `position` 呼叫參數格式錯誤，可能導致編譯失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri/src/webview/webview_window.rs:1317</code> [R03] `inner_size` 呼叫參數格式錯誤，可能導致編譯失敗</summary>

在 `window_features` 方法中，`self.window_builder.inner_size(size.width,    size.height);` 的參數之間有多餘空格，這違反了 rustfmt 格式規範（R03），且可能導致編譯器解析錯誤。建議移除多餘空格，改為 `self.window_builder.inner_size(size.width, size.height);`。

**判斷依據**：diff 中新增行：`+      self.window_builder = self.window_builder.inner_size(size.width,    size.height);`，參數間有多餘空格。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-runtime-wry/src/lib.rs:1718</code> `SetCookie` 訊息與方法名稱不一致，可能導致 cookie 刪除失敗</summary>

在 `delete_cookie` 方法中，原本傳送 `WebviewMessage::DeleteCookie`，現在改為 `WebviewMessage::SetCookie`。這可能導致刪除 cookie 的操作實際上變成設定 cookie，造成功能錯誤。請確認此變更是否為預期，若不是，應改回 `DeleteCookie`。

**判斷依據**：diff 中變更：`-        WebviewMessage::DeleteCookie(cookie.clone().into_owned()),` 改為 `+        WebviewMessage::SetCookie(cookie.into_owned()),`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri/src/webview/webview_window.rs:1321</code> [R03] `position` 呼叫參數格式錯誤，可能導致編譯失敗</summary>

在 `window_features` 方法中，`self.window_builder.position(position.x,position.y);` 的參數之間缺少空格，違反 rustfmt 格式規範（R03）。建議改為 `self.window_builder.position(position.x, position.y);`。

**判斷依據**：diff 中新增行：`+      self.window_builder = self.window_builder.position(position.x,position.y);`，參數間缺少空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5508 (cache hit 5504) ｜ completion tokens 843 ｜ PR #10</sub>