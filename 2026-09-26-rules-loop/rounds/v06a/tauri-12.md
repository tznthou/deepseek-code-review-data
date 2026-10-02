<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 macOS 檔案關聯的內容類型與匯出類型支援，包含 CLI 設定、schema 更新與 bundler 實作。主要風險在於 `create_info_plist` 中對 `ext` 為空時的處理邏輯可能導致 `CFBundleTypeExtensions` 被錯誤省略，以及 `expect` 取代 `unwrap_or` 可能造成 panic。此外，`UTTypeTagSpecification` 的 `public.filename-extension` 使用 `ext` 而非 `exported_type` 的內容，可能與預期不符。建議修正這些問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷錯誤導致 CFBundleTypeExtensions 永遠不會被加入 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 取代 unwrap_or 可能導致 panic | 0.85 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:290` | UTTypeTagSpecification 使用 ext 而非 exported_type 的內容 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1202` | 缺少 serde 別名以支援 kebab-case 設定 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷錯誤導致 CFBundleTypeExtensions 永遠不會被加入</summary>

在 `create_info_plist` 中，原本的程式碼會無條件加入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty()` 才加入。這會導致當 `ext` 非空時（正常情況），`CFBundleTypeExtensions` 不會被寫入 Info.plist，使得檔案關聯失效。

**失敗情境**：任何有設定 `ext` 的檔案關聯，在 macOS 上將無法正確關聯副檔名。

**建議修法**：移除 `if association.ext.is_empty()` 條件，恢復原本的無條件加入，或改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中原本的 `dict.insert("CFBundleTypeExtensions"...)` 被包在 `if association.ext.is_empty()` 內，但 `ext` 通常非空，因此該屬性將被省略。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 取代 unwrap_or 可能導致 panic</summary>

原本的程式碼使用 `unwrap_or(&association.ext[0].0)` 來提供預設名稱，修改後改為 `expect("File association must have a name")`。如果 `name` 為 `None` 且 `ext` 為空，程式會 panic。雖然 schema 可能要求 `name` 或 `ext` 至少一個存在，但此處的 panic 訊息不夠明確，且可能因設定錯誤而導致 bundler 崩潰。

**失敗情境**：使用者設定了一個沒有 `name` 且 `ext` 為空的檔案關聯，執行 bundler 時會 panic。

**建議修法**：保留原本的 `unwrap_or` 邏輯，或改用更安全的錯誤處理（例如回傳 `Result`）。

**判斷依據**：diff 中原本的 `unwrap_or(&association.ext[0].0)` 被替換為 `expect`，若 `ext` 為空則會 panic。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:290</code> UTTypeTagSpecification 使用 ext 而非 exported_type 的內容</summary>

在建構 `UTExportedTypeDeclarations` 時，`UTTypeTagSpecification` 的 `public.filename-extension` 使用了 `association.ext`，但此處的 `exported_type` 是針對自訂類型，其副檔名應該來自 `association.ext` 本身，這部分可能正確。然而，若 `association.ext` 為空（例如僅透過 `contentTypes` 關聯），則 `public.filename-extension` 會是空陣列，可能導致類型無法被正確識別。

**失敗情境**：使用者定義了一個 `exportedType` 但未指定 `ext`，僅依賴 `contentTypes`，則產生的 `UTExportedTypeDeclarations` 會缺少有效的副檔名標籤。

**建議修法**：確認此處是否應使用 `exported_type` 中的某個欄位，或允許 `ext` 為空時省略 `public.filename-extension`。

**判斷依據**：diff 中 `UTTypeTagSpecification` 的 `public.filename-extension` 直接使用 `association.ext`，但未處理 `ext` 為空的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1202</code> 缺少 serde 別名以支援 kebab-case 設定</summary>

新增的 `content_types` 欄位使用了 `#[serde(alias = "content-types")]`，但 `exported_type` 欄位沒有對應的別名（例如 `exported-type`）。在 Tauri 設定檔中，其他欄位通常使用 kebab-case，這可能導致使用者在 JSON 設定檔中使用 `exported-type` 時無法正確解析。

**失敗情境**：使用者在 `tauri.conf.json` 中寫 `"exported-type": {...}` 會導致反序列化錯誤。

**建議修法**：為 `exported_type` 加上 `#[serde(alias = "exported-type")]`。

**判斷依據**：diff 中 `exported_type` 欄位沒有 `serde(alias)`，而其他欄位如 `content_types` 有。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8161 (cache hit 6016) ｜ completion tokens 1542 ｜ PR #12</sub>