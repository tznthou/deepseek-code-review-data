<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 `contentTypes` 與 `exportedType` 支援，並更新了 schema、範例與變更日誌。主要風險在於 `CFBundleTypeExtensions` 的條件判斷邏輯反了，導致有副檔名的關聯不會寫入該鍵；此外 `CFBundleTypeName` 改用 `expect` 可能造成 panic。整體功能方向正確，但需修正上述問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | CFBundleTypeExtensions 條件判斷邏輯相反 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1184` | content_types 欄位缺少 serde 別名 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> CFBundleTypeExtensions 條件判斷邏輯相反</summary>

程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，這與預期相反。當副檔名清單為空時，不應插入該鍵；反之，當有副檔名時才應插入。目前的行為會導致所有有副檔名的關聯都不會寫入 `CFBundleTypeExtensions`，使得 macOS 無法正確建立檔案關聯。

建議改為 `if !association.ext.is_empty() { ... }`。

**判斷依據**：diff 中新增的條件判斷為 `if association.ext.is_empty()`，但插入的內容是基於 `association.ext` 的陣列，邏輯上應在有副檔名時才插入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。如果使用者未在設定中提供 `name` 且 `ext` 為空，程式會 panic。雖然 schema 可能要求 `name` 或 `ext` 至少一個存在，但此處的變更增加了執行時錯誤的風險。建議保留原本的 fallback 邏輯，或改為更安全的處理方式。

**判斷依據**：diff 中將原本的 `unwrap_or(&association.ext[0].0)` 改為 `expect`，若 `name` 為 None 且 `ext` 為空則會 panic。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1184</code> content_types 欄位缺少 serde 別名</summary>

新增的 `content_types` 欄位使用了 `#[serde(alias = "content-types")]`，但其他欄位如 `exported_type` 沒有對應的別名。這可能導致使用 kebab-case 的設定檔無法正確解析。建議檢查是否所有新增欄位都應提供一致的別名。

**判斷依據**：diff 中僅對 `content_types` 添加了別名，而 `exported_type` 未添加，可能造成不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6089 (cache hit 6016) ｜ completion tokens 912 ｜ PR #12</sub>