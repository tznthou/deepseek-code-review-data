<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的 file associations 新增了 content type 與 exported type 支援，包含 Rust 結構、Info.plist 生成邏輯、JSON schema 與範例更新。主要風險在於 `create_info_plist` 中對 `ext` 為空時的處理邏輯有誤，可能導致 `CFBundleTypeExtensions` 被錯誤省略，且 `expect` 的使用可能造成 panic。此外，部分新增欄位缺少 `#[serde(default)]`，可能破壞向後相容性。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷錯誤導致 CFBundleTypeExtensions 被省略 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.90 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1185` | 新增欄位缺少 serde default 可能破壞向後相容性 | 0.85 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1216` | ExportedFileAssociation 的 conforms_to 欄位缺少 serde default | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:271` | UTExportedTypeDeclarations 可能包含不完整的條目 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷錯誤導致 CFBundleTypeExtensions 被省略</summary>

在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，但修改後被包在 `if association.ext.is_empty()` 內。這導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入，造成 macOS 無法正確關聯檔案類型。

**失敗情境**：任何設定了 `ext` 的 file association（例如 `["png"]`）在產生的 Info.plist 中將缺少 `CFBundleTypeExtensions`，導致應用程式無法開啟該類型的檔案。

**建議**：將條件改為 `if !association.ext.is_empty()`，或直接移除條件，恢復原本的無條件插入。

**判斷依據**：diff 中原本的 `dict.insert("CFBundleTypeExtensions"...)` 被包進 `if association.ext.is_empty()`，但邏輯上應該是非空時才插入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

將原本的 `unwrap_or(&association.ext[0].0)` 改為 `expect("File association must have a name")`。若 `name` 為 `None` 且 `ext` 為空，程式會 panic。雖然 `ext` 為空的情況可能不常見，但這是一個潛在的崩潰點。

**失敗情境**：使用者設定了一個 file association 但未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議**：改用更安全的處理方式，例如使用 `unwrap_or_default()` 或提供預設值，或明確驗證 `ext` 非空。

**判斷依據**：diff 中原本的 `unwrap_or(&association.ext[0].0)` 被替換為 `expect`，而 `ext` 可能為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1185</code> 新增欄位缺少 serde default 可能破壞向後相容性</summary>

`FileAssociation` 新增了 `content_types` 和 `exported_type` 欄位，但沒有加上 `#[serde(default)]`。這會導致舊的設定檔（沒有這些欄位）在反序列化時失敗。

**失敗情境**：使用者使用舊版 `tauri.conf.json`，其中 file association 沒有 `contentTypes` 或 `exportedType`，升級後會出現反序列化錯誤。

**建議**：為這兩個欄位加上 `#[serde(default)]`，使其成為可選欄位。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]`，而其他可選欄位（如 `name`）都有。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1216</code> ExportedFileAssociation 的 conforms_to 欄位缺少 serde default</summary>

`ExportedFileAssociation` 的 `conforms_to` 欄位為 `Option<Vec<String>>`，但沒有 `#[serde(default)]`。如果 JSON 中省略該欄位，反序列化會失敗。

**失敗情境**：使用者在 `exportedType` 中只提供 `identifier`，未提供 `conformsTo`，會導致設定檔解析錯誤。

**建議**：加上 `#[serde(default)]`。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:271</code> UTExportedTypeDeclarations 可能包含不完整的條目</summary>

在建立 `exported_associations` 時，只對有 `exported_type` 的 association 進行處理，但未檢查 `ext` 是否為空。若 `ext` 為空，`UTTypeTagSpecification` 中的 `public.filename-extension` 會是空陣列，可能導致無效的類型宣告。

**失敗情境**：使用者定義了 `exportedType` 但未提供 `ext`，生成的 Info.plist 中會有一個空的 `public.filename-extension` 陣列。

**建議**：在處理 exported type 時，驗證 `ext` 非空，或提供合理的預設值。

**判斷依據**：diff 中未對 `ext` 進行檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8171 (cache hit 8064) ｜ completion tokens 1594 ｜ PR #12</sub>