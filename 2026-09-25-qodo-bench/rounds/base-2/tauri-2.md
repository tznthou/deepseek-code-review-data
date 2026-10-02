<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本從網路下載的 linuxdeploy 外掛腳本改為內嵌於程式碼中，以解決 429 錯誤。主要風險在於腳本中的路徑處理與權限設定，可能導致打包失敗或安全性問題。建議先修正 `write_and_make_executable` 的順序問題，並確認腳本中的路徑變數是否正確。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312` | 權限設定在寫入前執行，導致檔案權限錯誤 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238` | linuxdeploy 下載 URL 使用錯誤的架構變數 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75` | helpers_target_dir 路徑可能錯誤 | 0.75 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243` | gtk 外掛腳本存在時仍會覆寫 | 0.70 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:326` | 使用 sed 對二進位檔案進行替換可能損壞檔案 | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:320` | gio_extras_dir 可能為空導致匯出錯誤 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312</code> 權限設定在寫入前執行，導致檔案權限錯誤</summary>

在 `write_and_make_executable` 函式中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會失敗；若檔案已存在，`write` 會覆蓋內容但保留先前設定的權限，可能導致權限不符合預期。應先寫入檔案再設定權限。

**判斷依據**：diff 中顯示原本的順序是先 `fs::write` 再 `fs::set_permissions`，但修改後順序顛倒。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238</code> linuxdeploy 下載 URL 使用錯誤的架構變數</summary>

原本使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為 `arch`。若 `arch` 為 i686，則會下載不存在的 i686 版本，導致下載失敗。應保留 `linuxdeploy_arch`。

**判斷依據**：diff 中將 `{linuxdeploy_arch}` 改為 `{arch}`，但 `linuxdeploy_arch` 的定義是為了解決 i686 架構名稱不一致的問題。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gstreamer.sh:75</code> helpers_target_dir 路徑可能錯誤</summary>

`helpers_target_dir` 設定為 `$APPDIR/usr/lib/gstreamer$GSTREAMER_VERSION/gstreamer-$GSTREAMER_VERSION`，但後續的 AppRun hook 中使用的路徑是 `$APPDIR/usr/lib/gstreamer1.0/gstreamer-1.0`。若 `GSTREAMER_VERSION` 不是 1.0，路徑會不一致。建議確認版本變數的使用。

**判斷依據**：diff 中該行定義了 helpers_target_dir，而後續 hook 中硬編碼了 1.0 路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243</code> gtk 外掛腳本存在時仍會覆寫</summary>

原本邏輯是當 `gtk` 檔案不存在時才下載，但修改後變成當檔案存在時才寫入內嵌腳本。這會導致已存在的檔案被覆寫，可能不是預期行為。應改為 `if !gtk.exists()`。

**判斷依據**：diff 中條件從 `!gtk.exists()` 改為 `gtk.exists()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:326</code> 使用 sed 對二進位檔案進行替換可能損壞檔案</summary>

最後一行使用 `sed -i` 對 `libwebkit*` 檔案進行路徑替換，但這些是二進位檔案，直接使用 sed 可能破壞檔案內容。應使用 `patchelf` 或類似工具處理。

**判斷依據**：diff 中新增了此行，對二進位檔案使用 sed 是危險的。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/linux/appimage/linuxdeploy-plugin-gtk.sh:320</code> gio_extras_dir 可能為空導致匯出錯誤</summary>

`gio_extras_dir` 由 `find` 取得，若找不到 `libgiognutls.so`，變數會是空字串，後續的 `export GIO_EXTRA_MODULES` 會設定錯誤路徑。建議加入檢查。

**判斷依據**：diff 中新增此行，未處理空值情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9410 (cache hit 9344) ｜ completion tokens 1531 ｜ PR #2</sub>