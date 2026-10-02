<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 支援，並更新了 schema、範例與變更日誌。主要風險在於 `create_info_plist` 中對 `ext` 為空時的處理邏輯可能導致 `CFBundleTypeExtensions` 被錯誤省略，以及 `expect` 的使用可能造成 panic。此外，部分新增的公開 API 缺少文件註解，且變更日誌格式可能不符合 covector 規範。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 當 `ext` 為空時，`CFBundleTypeExtensions` 不會被加入，可能導致檔案關聯失效 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 `expect` 可能導致 panic，應改用更安全的處理方式 | 0.70 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1185` | [R07] 新增的公開欄位 `content_types` 缺少文件註解 | 0.60 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1202` | [R07] 新增的公開欄位 `exported_type` 缺少文件註解 | 0.60 |
| 🔸 | Minor | `.changes/file-association-content-type.md:2` | [R13] 變更日誌格式可能不符合 covector 規範 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 當 `ext` 為空時，`CFBundleTypeExtensions` 不會被加入，可能導致檔案關聯失效</summary>

在 `create_info_plist` 中，原本的程式碼會無條件加入 `CFBundleTypeExtensions`，但修改後只有在 `association.ext.is_empty()` 為 false 時才會加入。如果使用者設定了一個沒有副檔名的檔案關聯（例如只依賴 content type），則產生的 Info.plist 將缺少 `CFBundleTypeExtensions`，可能導致該關聯無法正常運作。建議改為：若 `ext` 為空，則加入空陣列或省略該鍵，但需確認 macOS 的行為。

**判斷依據**：diff 中原本的 `dict.insert("CFBundleTypeExtensions", ...)` 被包在 `if association.ext.is_empty()` 內，但條件判斷似乎相反（應為 `!association.ext.is_empty()`），且即使條件正確，當 `ext` 為空時仍應考慮是否要加入空陣列。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 `expect` 可能導致 panic，應改用更安全的處理方式</summary>

原本使用 `unwrap_or(&association.ext[0].0)` 來提供預設名稱，修改後改為 `expect("File association must have a name")`。如果使用者未提供 `name` 且 `ext` 為空，程式會 panic。建議改回使用 `unwrap_or` 搭配空字串或提供更明確的錯誤處理。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect`，但未處理 `ext` 為空的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1185</code> [R07] 新增的公開欄位 `content_types` 缺少文件註解</summary>

`FileAssociation` 結構體新增了 `content_types` 欄位，但沒有文件註解。根據規範 R07，所有公開 API 都應有文件說明。建議補上說明其用途與對應的 macOS 屬性。

**判斷依據**：diff 中新增的欄位沒有文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1202</code> [R07] 新增的公開欄位 `exported_type` 缺少文件註解</summary>

`FileAssociation` 結構體新增了 `exported_type` 欄位，但沒有文件註解。根據規範 R07，所有公開 API 都應有文件說明。建議補上說明其用途與對應的 macOS 屬性。

**判斷依據**：diff 中新增的欄位沒有文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.changes/file-association-content-type.md:2</code> [R13] 變更日誌格式可能不符合 covector 規範</summary>

變更日誌檔案使用了 `minor:feat` 的格式，但 covector 通常使用 `minor` 或 `patch` 等關鍵字。請確認此格式是否正確，否則可能導致版本管理工具無法解析。

**判斷依據**：diff 中新增的變更日誌檔案使用了 `minor:feat`，但未見其他類似用法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8171 (cache hit 8064) ｜ completion tokens 1238 ｜ PR #12</sub>