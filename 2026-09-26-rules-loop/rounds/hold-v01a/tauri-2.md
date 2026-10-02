<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本從網路下載的 linuxdeploy 外掛腳本改為內嵌於原始碼中，以避免 429 錯誤。主要風險在於新增的 shell 腳本中可能存在路徑處理、錯誤處理與相容性問題，以及 Rust 程式碼中錯誤型別未使用 thiserror、缺少文件註解等規範違反。建議優先修正 shell 腳本中的潛在錯誤，並調整 Rust 程式碼以符合專案規範。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75` | helpers_target_dir 路徑可能錯誤 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:149` | AppRun hook 中 GST_PLUGIN_SCANNER 路徑可能錯誤 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:316` | find 指令可能因權限或不存在檔案而失敗 | 0.70 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291` | [R08] 自訂錯誤型別未使用 thiserror | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:309` | [R07] 公開函式缺少文件註解 | 0.60 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312` | [R16] 使用 expect 可能導致 panic | 0.60 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:326` | sed 指令可能修改二進位檔案 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75</code> helpers_target_dir 路徑可能錯誤</summary>

在設定 helpers_target_dir 時，路徑為 `$APPDIR/usr/lib/gstreamer"$GSTREAMER_VERSION"/gstreamer-"$GSTREAMER_VERSION"`，但後續 AppRun hook 中使用的路徑是 `$APPDIR/usr/lib/gstreamer1.0/gstreamer-1.0`。若 GSTREAMER_VERSION 非 1.0，則 helpers 會被複製到錯誤的位置，導致執行時找不到 gst-plugin-scanner 等工具。建議確認路徑是否應為 `$APPDIR/usr/lib/gstreamer-$GSTREAMER_VERSION/gstreamer-$GSTREAMER_VERSION` 或統一使用變數。

**判斷依據**：diff 中第 74 行設定 helpers_target_dir，而第 146 行 AppRun hook 中寫死 gstreamer1.0/gstreamer-1.0。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:149</code> AppRun hook 中 GST_PLUGIN_SCANNER 路徑可能錯誤</summary>

在 AppRun hook 中，GST_PLUGIN_SCANNER_1_0 設定為 `${APPDIR}/usr/lib/gstreamer1.0/gstreamer-1.0/gst-plugin-scanner`，但實際複製 helpers 的目標路徑是 `$APPDIR/usr/lib/gstreamer$GSTREAMER_VERSION/gstreamer-$GSTREAMER_VERSION`。若 GSTREAMER_VERSION 為 1.0，則路徑為 `$APPDIR/usr/lib/gstreamer1.0/gstreamer-1.0`，與 hook 中一致；但若版本不同，則會找不到檔案。建議使用變數或確認版本固定為 1.0。

**判斷依據**：diff 中第 146 行設定 GST_PLUGIN_SCANNER_1_0，而第 74 行設定 helpers_target_dir 使用變數 GSTREAMER_VERSION。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:316</code> find 指令可能因權限或不存在檔案而失敗</summary>

在複製 libgiognutls.so 時，使用 `find /usr/lib* -name libgiognutls.so -exec mkdir -p "$APPDIR"/"$(dirname '{}')" \; -exec cp --parents '{}' "$APPDIR/" \; || true`。此指令若遇到權限不足或檔案不存在，會因為 `|| true` 而忽略錯誤，可能導致後續 GIO_EXTRA_MODULES 設定錯誤。建議檢查 find 的輸出並處理錯誤，或改用更穩健的方式。

**判斷依據**：diff 中第 327 行，使用 || true 忽略所有錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291</code> [R08] 自訂錯誤型別未使用 thiserror</summary>

新增的 FileWriteError 型別手動實作了 Display 和 Error trait，但專案規範 R08 要求使用 thiserror 來定義錯誤型別。建議改用 `#[derive(thiserror::Error)]` 並使用 `#[error(...)]` 屬性來簡化程式碼並符合規範。

**判斷依據**：diff 中第 281-295 行手動實作 Display 和 Error。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:309</code> [R07] 公開函式缺少文件註解</summary>

write_and_make_executable 函式是公開的（pub fn），但沒有文件註解。根據規範 R07，所有公開 API 都應該有 /// 文件說明其用途、參數和回傳值。建議補充文件。

**判斷依據**：diff 中第 297 行，函式為 pub fn 但無文件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312</code> [R16] 使用 expect 可能導致 panic</summary>

在 write_and_make_executable 中，使用 fs::set_permissions 和 fs::write 並以 map_err 處理錯誤，但沒有使用 expect 或 unwrap。然而，函式簽名回傳 Result<(), FileWriteError>，但內部可能因為其他原因 panic？實際上沒有直接使用 expect，但建議確認所有可能的錯誤都被妥善處理。

**判斷依據**：diff 中第 299-300 行，使用 ? 傳播錯誤，但未見 expect。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:326</code> sed 指令可能修改二進位檔案</summary>

使用 `find "$APPDIR"/usr/lib* -name 'libwebkit*' -exec sed -i -e "s|/usr|././|g" '{}' \;` 來修改 libwebkit 檔案中的絕對路徑。sed 通常用於文字檔，若 libwebkit 是二進位檔，此操作可能損壞檔案。建議確認檔案類型或使用更安全的工具。

**判斷依據**：diff 中第 327 行，對 libwebkit* 檔案執行 sed。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11492 (cache hit 9344) ｜ completion tokens 2067 ｜ PR #2</sub>