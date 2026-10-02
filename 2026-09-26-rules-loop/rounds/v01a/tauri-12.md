<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 contentTypes 與 exportedType 支援，並更新了對應的 schema、範例與變更紀錄。主要風險在於 `create_info_plist` 中對 `association.ext` 為空時的處理邏輯可能導致 panic，且 `CFBundleTypeExtensions` 的條件判斷似乎寫反了。此外，`FileAssociation` 新增的欄位未提供預設值，可能造成反序列化錯誤。建議優先修正這些正確性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷寫反，導致 ext 為空時仍插入 CFBundleTypeExtensions | 0.95 |
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.90 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1185` | 新增欄位未提供 serde default，可能導致反序列化失敗 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:271` | UTTypeTagSpecification 中 public.filename-extension 可能為空陣列 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷寫反，導致 ext 為空時仍插入 CFBundleTypeExtensions</summary>

在 `create_info_plist` 中，原本的程式碼是直接插入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty() { ... }`。這會導致當 `ext` 為空時才插入該鍵，而當 `ext` 有值時反而跳過，與預期行為完全相反。

**失敗情境**：若某個 file association 只設定了 `contentTypes` 而沒有 `ext`（這是此 PR 新增的合法情境），則 `CFBundleTypeExtensions` 會被錯誤地加入一個空陣列；反之，若設定了 `ext`，則該鍵會被遺漏，導致 macOS 無法正確關聯副檔名。

**建議**：將條件改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中原本的 `dict.insert("CFBundleTypeExtensions"...)` 被包在 `if association.ext.is_empty()` 內，但從上下文判斷應為 `!is_empty()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

原本的程式碼使用 `unwrap_or(&association.ext[0].0)` 來提供預設名稱，但修改後改為 `expect("File association must have a name")`。這表示當 `name` 為 `None` 且 `ext` 為空時，程式會直接 panic。

**失敗情境**：若使用者設定了一個 file association，只提供 `contentTypes` 而沒有 `ext` 和 `name`（這是此 PR 允許的新用法），在建置 macOS bundle 時就會 panic。

**建議**：提供一個合理的預設值，例如若 `ext` 非空則使用第一個副檔名，否則使用 `contentTypes` 的第一個項目，或直接使用空字串。

**判斷依據**：diff 中將原本的 `unwrap_or(&association.ext[0].0)` 改為 `expect(...)`，且 `ext` 可能為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1185</code> 新增欄位未提供 serde default，可能導致反序列化失敗</summary>

`FileAssociation` 新增了 `content_types` 和 `exported_type` 兩個欄位，但沒有加上 `#[serde(default)]`。這表示現有的 `tauri.conf.json` 若未包含這些欄位，在反序列化時會出錯。

**失敗情境**：使用者升級到新版本後，若其設定檔中沒有這兩個新欄位，程式啟動時會因為缺少欄位而 panic 或回傳錯誤。

**建議**：為這兩個欄位加上 `#[serde(default)]`，以維持向後相容性。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性，而其他欄位如 `rank` 有。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:271</code> UTTypeTagSpecification 中 public.filename-extension 可能為空陣列</summary>

在建構 `UTTypeTagSpecification` 時，直接將 `association.ext` 的所有項目放入 `public.filename-extension` 陣列。若 `ext` 為空，則會產生空陣列，這在 macOS 的 UTI 宣告中可能是不合法的。

**失敗情境**：若使用者只設定 `contentTypes` 而沒有 `ext`，則產生的 Info.plist 中 `UTExportedTypeDeclarations` 會包含一個空的 `public.filename-extension`，可能導致系統無法正確識別該類型。

**建議**：僅在 `ext` 非空時才加入 `public.filename-extension` 鍵。

**判斷依據**：diff 中新增的程式碼直接使用 `association.ext`，未檢查是否為空。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8171 (cache hit 6016) ｜ completion tokens 1433 ｜ PR #12</sub>