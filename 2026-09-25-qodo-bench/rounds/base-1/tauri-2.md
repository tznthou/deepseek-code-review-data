<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 linuxdeploy 的 GTK 與 GStreamer 外掛腳本從執行時下載改為內嵌於原始碼中，以避免 GitHub raw 的 429 錯誤。主要風險在於腳本內嵌後若上游更新，需手動同步；且 `write_and_make_executable` 的執行順序變更可能導致權限設定失效。此外，腳本中有些路徑與變數處理可能造成打包失敗或非預期行為。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312` | write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238` | linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤 | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:316` | find 指令使用 -exec 搭配 dirname 可能無法正確處理含空格路徑 | 0.60 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:326` | sed 對 libwebkit 檔案進行二進位替換可能損壞檔案 | 0.60 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:157` | GStreamer 0.10 的 AppRun hook 使用了錯誤的路徑 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312</code> write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋</summary>

函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

**判斷依據**：diff 中顯示原本順序為 `fs::write` 後 `fs::set_permissions`，現在順序顛倒。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238</code> linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤</summary>

原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

**判斷依據**：diff 中原本使用 `linuxdeploy_arch`，現在改為 `arch`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:316</code> find 指令使用 -exec 搭配 dirname 可能無法正確處理含空格路徑</summary>

`find /usr/lib* -name libgiognutls.so -exec mkdir -p "$APPDIR"/"$(dirname '{}')" \; -exec cp --parents '{}' "$APPDIR/" \;` 中，`dirname '{}'` 在 find 的 -exec 中不會被 shell 展開，而是直接將 `{}` 傳給 dirname，可能導致路徑錯誤。建議改用 `-exec sh -c '...'` 或 `-execdir`。

**判斷依據**：diff 中新增的這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:326</code> sed 對 libwebkit 檔案進行二進位替換可能損壞檔案</summary>

`find "$APPDIR"/usr/lib* -name 'libwebkit*' -exec sed -i -e "s|/usr|././|g" '{}' \;` 直接對二進位檔案執行 sed 替換，可能破壞檔案內容。建議使用 `sed -i.bak` 或確認檔案為文字格式，或改用 `patchelf` 等工具。

**判斷依據**：diff 中新增的這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:157</code> GStreamer 0.10 的 AppRun hook 使用了錯誤的路徑</summary>

在 `GSTREAMER_VERSION == "0.10"` 的分支中，`GST_PLUGIN_SYSTEM_PATH_0_10` 被設定為 `${APPDIR}/usr/lib/gstreamer-1.0`，但 0.10 版本應使用 `gstreamer-0.10`。這可能導致 0.10 應用程式找不到外掛。

**判斷依據**：diff 中該行位於 0.10 分支。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9410 (cache hit 1536) ｜ completion tokens 1452 ｜ PR #2</sub>