<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 contentTypes 與 exportedType 支援，並更新了對應的 schema 與範例。主要風險在於 `create_info_plist` 中對 `association.name` 使用 `expect`，當使用者未提供 name 且 ext 為空時會導致 panic；此外，`CFBundleTypeExtensions` 的條件判斷邏輯可能顛倒，導致有副檔名時反而未寫入。建議修正這些邏輯並補充測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | CFBundleTypeExtensions 條件判斷可能顛倒 | 0.85 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1185` | content_types 與 exported_type 缺少 serde 別名 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

當 `association.name` 為 `None` 且 `association.ext` 為空時，`expect` 會觸發 panic。這會讓使用者在設定檔中未提供 name 且 ext 為空時，在建置階段直接崩潰。建議改回原本的 `unwrap_or(&association.ext[0].0)` 或提供更安全的 fallback（例如使用空字串或預設名稱）。

**判斷依據**：diff 中將原本的 `unwrap_or(&association.ext[0].0)` 改為 `expect("File association must have a name")`，但未處理 ext 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> CFBundleTypeExtensions 條件判斷可能顛倒</summary>

原本的程式碼無論 ext 是否為空都會寫入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty()` 才寫入，這似乎與預期相反。若 ext 非空，則不會寫入副檔名，可能導致 macOS 無法正確關聯檔案。請確認條件是否應為 `!association.ext.is_empty()`。

**判斷依據**：diff 中新增了 `if association.ext.is_empty()` 條件包住原本的寫入邏輯，但從語意上來看，應該是在 ext 非空時才寫入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1185</code> content_types 與 exported_type 缺少 serde 別名</summary>

新增的欄位 `content_types` 和 `exported_type` 在 struct 上使用了 `rename_all = "camelCase"`，但沒有像其他欄位（如 `mime_type`）加上 `serde(alias = "content-types")` 或 `serde(alias = "exported-type")`。這可能導致使用 kebab-case 的舊設定檔無法正確反序列化。建議加上別名以維持相容性。

**判斷依據**：diff 中新增的欄位沒有 `serde(alias)` 屬性，而其他欄位如 `mime_type` 有 `#[serde(alias = "mime-type")]`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8864 (cache hit 8832) ｜ completion tokens 912 ｜ PR #12</sub>