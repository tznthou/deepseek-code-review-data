<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本從網路下載的 linuxdeploy 外掛腳本改為內嵌於程式碼中，以解決 429 錯誤。主要風險在於 `write_and_make_executable` 函式中的操作順序變更：先設定權限再寫入檔案，若檔案已存在且不可寫，會導致權限設定失敗；若檔案不存在，則會建立一個權限為 0o770 的空檔案，之後寫入時可能因權限不足而失敗。此外，`linuxdeploy-plugin-gtk.sh` 中強制設定 `DEPLOY_GTK_VERSION=3`，可能影響非 GTK3 應用程式。整體而言，變更方向合理，但需修正上述問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312` | write_and_make_executable 操作順序錯誤導致檔案寫入失敗 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:90` | 強制設定 DEPLOY_GTK_VERSION=3 可能導致非 GTK3 應用程式打包失敗 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75` | helpers_target_dir 路徑可能錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312</code> write_and_make_executable 操作順序錯誤導致檔案寫入失敗</summary>

函式先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若目標檔案已存在且目前使用者無寫入權限，`set_permissions` 會失敗；若檔案不存在，`set_permissions` 會建立一個空檔案並設定權限為 0o770，但之後 `fs::write` 可能因權限不足而失敗。應先寫入檔案內容，再設定權限。

**判斷依據**：diff 中顯示原本的順序是 `fs::write` 後 `fs::set_permissions`，但新程式碼將兩者對調。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:90</code> 強制設定 DEPLOY_GTK_VERSION=3 可能導致非 GTK3 應用程式打包失敗</summary>

腳本中直接將 `DEPLOY_GTK_VERSION` 設為 3，並註解掉原本的自動偵測邏輯。若應用程式使用 GTK2 或 GTK4，此設定會導致後續處理錯誤或遺漏必要的函式庫。建議保留自動偵測或允許使用者覆寫。

**判斷依據**：diff 中新增此行，且上方原本的自動偵測程式碼被註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75</code> helpers_target_dir 路徑可能錯誤</summary>

`helpers_target_dir` 的組成為 `$APPDIR/usr/lib/gstreamer$GSTREAMER_VERSION/gstreamer-$GSTREAMER_VERSION`，但後續 AppRun hook 中使用的路徑是 `$APPDIR/usr/lib/gstreamer1.0/gstreamer-1.0`，兩者不一致。若 `GSTREAMER_VERSION` 非 1.0，可能導致找不到 helper 工具。

**判斷依據**：diff 中此行定義 helpers_target_dir，而後續 hook 寫死 gstreamer1.0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9374 (cache hit 9344) ｜ completion tokens 940 ｜ PR #2</sub>