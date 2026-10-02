<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本從網路下載的 linuxdeploy 外掛腳本改為內嵌於原始碼中，以避免 429 錯誤。主要風險在於新增的 shell 腳本缺乏錯誤處理與輸入驗證，且 Rust 程式碼中的錯誤處理與檔案寫入順序可能導致權限問題。建議優先修正 shell 腳本中的路徑處理與 Rust 中的檔案寫入順序。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75` | helpers_target_dir 路徑缺少斜線 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:316` | find 命令可能因權限不足而失敗 | 0.75 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312` | write_and_make_executable 先設定權限再寫入檔案 | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291` | 自訂錯誤型別未使用 thiserror | 0.60 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:326` | 使用 sed 修改二進位檔案可能損壞檔案 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75</code> helpers_target_dir 路徑缺少斜線</summary>

在 `helpers_target_dir` 的設定中，`gstreamer"$GSTREAMER_VERSION"` 與後續的 `/gstreamer-` 之間缺少斜線，導致路徑錯誤。例如當 `GSTREAMER_VERSION=1.0` 時，會產生 `.../gstreamer1.0/gstreamer-1.0`，但正確應為 `.../gstreamer-1.0/gstreamer-1.0`。這會使後續的 `mkdir -p` 建立錯誤的目錄結構，且複製的 helper 檔案會放在錯誤位置，導致 AppRun hook 中的 `GST_PLUGIN_SCANNER_1_0` 等路徑無法找到檔案。

**判斷依據**：diff 中第 85 行（新增檔案）的該行，與正確路徑格式比較，缺少斜線。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:316</code> find 命令可能因權限不足而失敗</summary>

`find /usr/lib* -name libgiognutls.so -exec mkdir -p "$APPDIR"/"$(dirname '{}')" \; -exec cp --parents '{}' "$APPDIR/" \; || true` 中的 `find` 若遇到無法讀取的目錄（例如權限不足），會輸出錯誤訊息但不會中斷（因為 `|| true`），但可能導致部分檔案未被複製。建議改用 `find` 的 `-readable` 或先檢查目錄權限，或改用 `rsync` 等更可靠的方式。

**判斷依據**：diff 中第 327 行（新增檔案）的該行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312</code> write_and_make_executable 先設定權限再寫入檔案</summary>

函式 `write_and_make_executable` 先呼叫 `fs::set_permissions` 設定權限，再呼叫 `fs::write` 寫入檔案。若檔案不存在，`set_permissions` 會失敗並回傳錯誤，導致無法建立檔案。應先寫入檔案再設定權限，或使用 `OpenOptions` 建立檔案後設定權限。

**判斷依據**：diff 中 mod.rs 第 281 行附近的變更，顯示順序顛倒。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291</code> 自訂錯誤型別未使用 thiserror</summary>

新增的 `FileWriteError` 手動實作 `Display` 和 `Error`，但專案規範 [R08] 要求使用 `thiserror`。建議改用 `#[derive(thiserror::Error)]` 來簡化程式碼並保持一致。

**判斷依據**：diff 中 mod.rs 新增的錯誤型別實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:326</code> 使用 sed 修改二進位檔案可能損壞檔案</summary>

`find "$APPDIR"/usr/lib* -name 'libwebkit*' -exec sed -i -e "s|/usr|././|g" '{}' \;` 對二進位檔案執行 `sed` 替換字串，可能破壞檔案內容。建議改用 `patchelf` 或 `chrpath` 等工具來修改 rpath，或確認此操作的必要性。

**判斷依據**：diff 中 gtk.sh 第 327 行（新增檔案）的該行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11492 (cache hit 11392) ｜ completion tokens 1513 ｜ PR #2</sub>