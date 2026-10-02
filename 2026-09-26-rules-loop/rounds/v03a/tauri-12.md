<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 的支援，並更新了對應的 schema、範例與變更紀錄。主要風險在於 `create_info_plist` 中對 `association.ext` 為空時的處理邏輯有誤，可能導致 panic 或產生無效的 plist；此外，`FileAssociation` 新增的欄位未設定 `#[serde(default)]`，可能造成向後相容性問題。建議先修正這些問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷錯誤：ext 為空時才插入 CFBundleTypeExtensions | 0.95 |
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.90 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1185` | 新增欄位未設定 serde default，可能破壞向後相容性 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1208` | ExportedFileAssociation 缺少 deny_unknown_fields 的 alias 處理 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷錯誤：ext 為空時才插入 CFBundleTypeExtensions</summary>

在 `create_info_plist` 中，原本的程式碼會無條件插入 `CFBundleTypeExtensions`，但修改後變成只有當 `association.ext.is_empty()` 為 true 時才插入。這與預期行為相反：當 `ext` 為空時，不應該插入該鍵；而當 `ext` 非空時，才應該插入。目前的寫法會導致：
- 當 `ext` 非空時，`CFBundleTypeExtensions` 不會被加入 plist，使得檔案關聯無法正確運作。
- 當 `ext` 為空時，會插入一個空陣列，可能導致無效的 plist。

建議改為 `if !association.ext.is_empty() { ... }`。

**判斷依據**：diff 中原本的 `dict.insert("CFBundleTypeExtensions", ...)` 被包在 `if association.ext.is_empty() { ... }` 內，但邏輯上應該是非空時才插入。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

原本使用 `unwrap_or(&association.ext[0].0)` 來提供預設名稱，但修改後改為 `expect("File association must have a name")`。如果 `association.name` 為 `None` 且 `association.ext` 為空，程式會 panic。雖然在大多數情況下 `ext` 不會為空，但這是一個潛在的崩潰點。建議保留原本的 fallback 邏輯，或改用更安全的處理方式。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect(...)`，移除了原本的 fallback。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1185</code> 新增欄位未設定 serde default，可能破壞向後相容性</summary>

`FileAssociation` 新增了 `content_types` 和 `exported_type` 欄位，但沒有加上 `#[serde(default)]`。這表示舊的設定檔如果沒有這兩個欄位，反序列化時會失敗。建議為這兩個欄位加上 `#[serde(default)]`，以維持向後相容性。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性，而其他可選欄位如 `name`、`description` 等都有。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1208</code> ExportedFileAssociation 缺少 deny_unknown_fields 的 alias 處理</summary>

`ExportedFileAssociation` 使用了 `deny_unknown_fields`，但 `conforms_to` 欄位設定了 `#[serde(alias = "conforms-to")]`。這可能導致使用 kebab-case 的設定檔（如 `conforms-to`）被拒絕，因為 alias 不會被 deny_unknown_fields 接受。建議確認 alias 與 deny_unknown_fields 的相容性，或移除 deny_unknown_fields。

**判斷依據**：diff 中新增的 struct 同時使用了 `deny_unknown_fields` 和欄位 alias。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8181 (cache hit 6016) ｜ completion tokens 1265 ｜ PR #12</sub>