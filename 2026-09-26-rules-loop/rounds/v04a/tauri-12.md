<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 的支援，包含 Rust 結構、JSON schema、Info.plist 生成邏輯與範例更新。主要風險在於 `create_info_plist` 中對 `association.ext` 為空時的處理：原本的 `unwrap_or(&association.ext[0].0)` 改為 `expect("File association must have a name")`，但 `name` 欄位是 `Option`，若使用者未提供 `name` 且 `ext` 為空，將導致 panic。此外，`CFBundleTypeExtensions` 的插入條件似乎寫反了，應在 `ext` 非空時才插入。建議優先修正這兩個問題，並補上對應的測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 當 ext 為空且 name 未提供時會 panic | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | CFBundleTypeExtensions 插入條件寫反 | 0.90 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1184` | 新增欄位未加上 serde(default) 可能導致反序列化失敗 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:293` | UTTypeTagSpecification 中 public.filename-extension 可能應為 public.filename-extensions | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:271` | UTTypeTagSpecification 中 public.filename-extension 的值應為字串陣列而非單一字串 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 當 ext 為空且 name 未提供時會 panic</summary>

原本的程式碼使用 `unwrap_or(&association.ext[0].0)`，在 `ext` 為空且 `name` 為 `None` 時會嘗試索引空陣列而 panic。此 PR 改為 `expect("File association must have a name")`，但 `name` 欄位仍是 `Option`，若使用者未提供 `name` 且 `ext` 為空，仍會 panic。應改為提供預設值或回傳錯誤，而非直接 panic。

**判斷依據**：diff 中將原本的 `unwrap_or(&association.ext[0].0)` 改為 `expect("File association must have a name")`，但 `name` 欄位在 `FileAssociation` 結構中仍是 `Option<String>`，且沒有其他預設值邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> CFBundleTypeExtensions 插入條件寫反</summary>

在 `create_info_plist` 中，原本的程式碼無條件插入 `CFBundleTypeExtensions`，但此 PR 改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（常見情況）反而沒有插入 `CFBundleTypeExtensions`，造成檔案關聯失效。應改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中新增的條件判斷為 `if association.ext.is_empty()`，但插入的內容是 `CFBundleTypeExtensions`，邏輯上應在 `ext` 非空時才插入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1184</code> 新增欄位未加上 serde(default) 可能導致反序列化失敗</summary>

`FileAssociation` 新增了 `content_types` 和 `exported_type` 欄位，但沒有加上 `#[serde(default)]`。若使用者的 `tauri.conf.json` 中沒有這些欄位（舊版設定），反序列化時會因為缺少欄位而失敗。建議加上 `#[serde(default)]` 以維持向後相容。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性，而其他 `Option` 欄位（如 `name`）也沒有，但此處是新增欄位，舊設定檔可能沒有這些鍵。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:293</code> UTTypeTagSpecification 中 public.filename-extension 可能應為 public.filename-extensions</summary>

在 `UTTypeTagSpecification` 中，使用的鍵是 `public.filename-extension`，但 Apple 的文件中常見的鍵是 `public.filename-extensions`（複數）。請確認正確的鍵名，否則可能導致 macOS 無法正確識別檔案副檔名。

**判斷依據**：diff 中新增的程式碼使用了 `public.filename-extension`，但根據 Apple 的 Uniform Type Identifiers 文件，標準鍵為 `public.filename-extensions`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:271</code> UTTypeTagSpecification 中 public.filename-extension 的值應為字串陣列而非單一字串</summary>

在 `UTTypeTagSpecification` 中，`public.filename-extension` 的值應為字串陣列，但目前的程式碼將 `association.ext` 轉換為 `Vec<String>` 後直接放入 `plist::Value::Array`，這看起來是正確的。但若 `association.ext` 為空，會產生空陣列，可能導致問題。建議確認空陣列是否合法。

**判斷依據**：diff 中新增的程式碼將 `association.ext` 轉換為陣列，但未處理空陣列的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7144 (cache hit 6016) ｜ completion tokens 1508 ｜ PR #12</sub>