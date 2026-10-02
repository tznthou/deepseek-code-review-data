<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 的支援，並更新了對應的 schema 與範例。主要風險在於 `create_info_plist` 中對 `association.ext` 為空時的處理邏輯有誤，可能導致 `CFBundleTypeExtensions` 未正確加入，且 `CFBundleTypeName` 的 fallback 改為 `expect` 可能造成 panic。此外，`exported_type` 欄位缺少 `#[serde(alias = "exported-type")]`，可能導致使用 kebab-case 的設定檔無法正確解析。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷錯誤導致 CFBundleTypeExtensions 永遠不會被加入 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.90 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1202` | 缺少 serde alias 導致 kebab-case 設定無法解析 | 0.85 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:271` | UTTypeConformsTo 應使用 exported_type.conforms_to 而非 association.content_types | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:271` | UTTypeTagSpecification 中 public.filename-extension 應使用 exported_type 的副檔名 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷錯誤導致 CFBundleTypeExtensions 永遠不會被加入</summary>

在 `create_info_plist` 中，原本的程式碼會將 `CFBundleTypeExtensions` 加入 dict，但修改後被包在 `if association.ext.is_empty()` 條件內。這導致只有當 `ext` 為空時才會加入該鍵，與預期行為相反。這會使得所有具有副檔名的檔案關聯在產生的 Info.plist 中缺少 `CFBundleTypeExtensions`，導致 macOS 無法正確關聯檔案類型。

建議將條件改為 `if !association.ext.is_empty()`，或直接移除條件，恢復原本的邏輯。

**判斷依據**：diff 中新增的 `if association.ext.is_empty()` 條件包住了原本的 `CFBundleTypeExtensions` 插入邏輯，但 `ext` 為空時不應加入該鍵，且非空時才應加入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

原本的程式碼使用 `unwrap_or(&association.ext[0].0)` 來提供預設名稱，但修改後改為 `expect("File association must have a name")`。如果 `name` 為 `None` 且 `ext` 為空，程式會 panic。雖然在大多數情況下 `ext` 不會為空，但這是一個潛在的崩潰點。建議保留原本的 fallback 邏輯，或使用更安全的處理方式。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect`，移除了對空 `ext` 的保護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1202</code> 缺少 serde alias 導致 kebab-case 設定無法解析</summary>

新增的 `exported_type` 欄位沒有加上 `#[serde(alias = "exported-type")]`。在 Tauri 設定檔中，欄位通常使用 kebab-case（例如 `content-types`），但此欄位若使用 `exported-type` 將無法被正確解析，導致設定被忽略。建議加上 alias 以維持一致性。

**判斷依據**：同結構中其他欄位如 `content_types` 有 `#[serde(alias = "content-types")]`，但 `exported_type` 沒有。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:271</code> UTTypeConformsTo 應使用 exported_type.conforms_to 而非 association.content_types</summary>

在建構 `UTExportedTypeDeclarations` 時，`UTTypeConformsTo` 的值取自 `association.content_types`，但根據語意，應該使用 `exported_type.conforms_to`。`content_types` 是用於 `LSItemContentTypes` 的，而 `conforms_to` 才是定義此類型符合哪些系統類型的欄位。這可能導致生成的 plist 不正確。

**判斷依據**：在 `exported_type` 的處理中，使用了 `association.content_types` 來填充 `UTTypeConformsTo`，但 `ExportedFileAssociation` 結構中有 `conforms_to` 欄位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:271</code> UTTypeTagSpecification 中 public.filename-extension 應使用 exported_type 的副檔名</summary>

在建構 `UTTypeTagSpecification` 時，使用了 `association.ext` 來填充 `public.filename-extension`。但若 `exported_type` 存在，其副檔名可能與 `association.ext` 不同（例如 `exported_type` 可能定義了多個副檔名）。建議確認此處是否應使用 `exported_type` 的相關欄位。

**判斷依據**：`ExportedFileAssociation` 結構中沒有副檔名欄位，但 `association.ext` 可能包含多個副檔名，而 exported type 通常只對應一個。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7144 (cache hit 7040) ｜ completion tokens 1561 ｜ PR #12</sub>