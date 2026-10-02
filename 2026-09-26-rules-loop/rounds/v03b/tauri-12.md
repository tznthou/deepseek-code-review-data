<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 支援，並更新了設定結構與範例。主要風險在於 `create_info_plist` 中對 `CFBundleTypeExtensions` 的條件判斷邏輯錯誤（應為 `!is_empty()` 才插入），以及使用 `expect` 取代原本的 fallback 可能導致 panic。此外，`UTTypeTagSpecification` 的 `public.filename-extension` 未處理空陣列，可能產生無效的 plist。建議修正這些問題後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷錯誤：應在 ext 非空時才插入 CFBundleTypeExtensions | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 取代 fallback 可能導致 panic | 0.90 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:289` | UTTypeTagSpecification 的 public.filename-extension 未處理空陣列 | 0.85 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1185` | 新增欄位未標記 serde(default) 可能導致反序列化失敗 | 0.70 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1216` | ExportedFileAssociation 缺少 serde(default) 可能導致反序列化失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷錯誤：應在 ext 非空時才插入 CFBundleTypeExtensions</summary>

在 `create_info_plist` 中，原本的程式碼會無條件插入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty()` 才插入，這與預期相反。當 `ext` 為空時，會插入一個空陣列，可能導致 macOS 無法正確處理檔案關聯；當 `ext` 非空時，反而會遺漏必要的 `CFBundleTypeExtensions` 鍵。

**失敗情境**：使用者設定一個只有 `contentTypes` 而沒有 `ext` 的關聯時，會產生空的 `CFBundleTypeExtensions`，可能導致該關聯無法被系統識別。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中原本的無條件插入被改為 `if association.ext.is_empty()`，但邏輯上應為非空才插入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 取代 fallback 可能導致 panic</summary>

原本的程式碼在 `name` 為 `None` 時會使用 `association.ext[0]` 作為 fallback，但修改後改為 `expect("File association must have a name")`。如果使用者未提供 `name` 且 `ext` 為空（例如只使用 `contentTypes`），程式會 panic。

**失敗情境**：設定檔中某個關聯只有 `contentTypes` 而沒有 `name` 和 `ext`，執行 bundler 時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用 `unwrap_or_else` 提供更安全的預設值。

**判斷依據**：diff 中原本的 `unwrap_or(&association.ext[0].0)` 被改為 `expect`，且 `ext` 可能為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:289</code> UTTypeTagSpecification 的 public.filename-extension 未處理空陣列</summary>

在建構 `UTTypeTagSpecification` 時，直接將 `association.ext` 轉換為陣列插入，但若 `ext` 為空，會產生一個空的 `public.filename-extension` 陣列。根據 Apple 的文件，`public.filename-extension` 應為非空陣列，否則可能導致類型宣告無效。

**失敗情境**：使用者定義一個 exported type 但未提供任何副檔名，產生的 plist 可能無法被 macOS 正確解析。

**建議修法**：僅在 `ext` 非空時才插入 `public.filename-extension`，或提供其他必要的 tag specification。

**判斷依據**：diff 中新增的程式碼未檢查 `ext` 是否為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1185</code> 新增欄位未標記 serde(default) 可能導致反序列化失敗</summary>

在 `FileAssociation` 結構中新增的 `content_types` 和 `exported_type` 欄位沒有加上 `#[serde(default)]`。如果使用者的設定檔是舊版格式，缺少這些欄位時，反序列化會失敗。

**失敗情境**：使用者使用舊版 `tauri.conf.json`，其中沒有 `contentTypes` 或 `exportedType` 欄位，執行 CLI 時會出現反序列化錯誤。

**建議修法**：為這兩個欄位加上 `#[serde(default)]`，或使用 `Option` 並配合 `#[serde(default)]`。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1216</code> ExportedFileAssociation 缺少 serde(default) 可能導致反序列化失敗</summary>

`ExportedFileAssociation` 結構中的 `conforms_to` 欄位沒有加上 `#[serde(default)]`。如果使用者的設定檔中省略了 `conformsTo`，反序列化會失敗。

**失敗情境**：使用者定義 exported type 但未提供 `conformsTo`，執行 CLI 時會出現反序列化錯誤。

**建議修法**：為 `conforms_to` 加上 `#[serde(default)]`。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8181 (cache hit 8064) ｜ completion tokens 1632 ｜ PR #12</sub>