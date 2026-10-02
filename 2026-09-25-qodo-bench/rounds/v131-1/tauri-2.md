<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本從網路下載的 linuxdeploy 外掛腳本改為內嵌於程式碼中，以避免 429 錯誤。主要風險在於腳本內容的維護與正確性，以及 Rust 程式碼中邏輯反轉與權限設定順序的變更。最關鍵的問題是 `prepare_tools` 中 GTK 腳本的條件判斷寫反，導致已存在的腳本會被覆寫，而未存在的腳本不會被建立。此外，`write_and_make_executable` 改為先設定權限再寫入，可能造成權限設定失敗或檔案內容被覆蓋。建議優先修正這些邏輯錯誤。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243` | GTK 腳本存在性檢查邏輯反轉 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312` | write_and_make_executable 先設定權限再寫入可能導致問題 | 0.85 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75` | helpers_target_dir 路徑可能錯誤 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:90` | DEPLOY_GTK_VERSION 被強制設為 3，可能導致無法支援其他 GTK 版本 | 0.75 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:230` | sed 指令可能因檔案不存在而失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243</code> GTK 腳本存在性檢查邏輯反轉</summary>

原本的邏輯是「若檔案不存在，則下載並寫入」，但修改後變成「若檔案存在，則寫入內嵌內容」。這會導致：
1. 當檔案不存在時，不會建立該檔案，後續執行可能因缺少腳本而失敗。
2. 當檔案已存在時，會用內嵌內容覆蓋，可能破壞使用者自訂的腳本。

建議改回 `if !gtk.exists()` 的條件。

**判斷依據**：diff 中顯示原本的 `if !gtk.exists()` 被改為 `if gtk.exists()`，且內部的下載動作改為 `include_bytes!`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312</code> write_and_make_executable 先設定權限再寫入可能導致問題</summary>

函式改為先執行 `fs::set_permissions` 再執行 `fs::write`。若檔案不存在，`set_permissions` 會失敗並回傳錯誤，導致函式提前返回，檔案永遠不會被建立。此外，即使檔案存在，先設定權限再寫入也可能在寫入過程中因權限不足而失敗。建議維持原本的先寫入再設定權限的順序。

**判斷依據**：diff 中原本的 `fs::write` 在前，`fs::set_permissions` 在後，修改後順序對調。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75</code> helpers_target_dir 路徑可能錯誤</summary>

`helpers_target_dir` 的組成為 `$APPDIR/usr/lib/gstreamer$GSTREAMER_VERSION/gstreamer-$GSTREAMER_VERSION`，但後續 AppRun hook 中使用的路徑是 `$APPDIR/usr/lib/gstreamer1.0/gstreamer-1.0`。若 `GSTREAMER_VERSION` 不是 `1.0`，路徑會不一致，導致找不到 helper 工具。建議確認路徑是否正確，或使用變數統一。

**判斷依據**：diff 中該行定義了 helpers_target_dir，而後續 hook 中寫死 `gstreamer1.0`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:90</code> DEPLOY_GTK_VERSION 被強制設為 3，可能導致無法支援其他 GTK 版本</summary>

原本的 `DEPLOY_GTK_VERSION` 可以透過環境變數設定，但此處被硬編碼為 `3`。這會使得使用 GTK2 或 GTK4 的應用程式無法正確打包。建議保留原本的環境變數設定，或提供明確的設定方式。

**判斷依據**：diff 中該行取代了原本的 `DEPLOY_GTK_VERSION="${DEPLOY_GTK_VERSION:-0}"`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:230</code> sed 指令可能因檔案不存在而失敗</summary>

`sed -i "s|$gtk3_libdir/3.0.0/immodules/||g" "$APPDIR/$gtk3_immodules_cache_file"` 在執行前未檢查檔案是否存在。若 `gtk3_immodules_cache_file` 不存在，sed 會報錯並可能中斷腳本（因為 `set -e`）。建議先檢查檔案存在再執行 sed。

**判斷依據**：diff 中該行直接執行 sed，且腳本開頭有 `set -e`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9374 (cache hit 1408) ｜ completion tokens 1477 ｜ PR #2</sub>