<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 的支援，並更新了對應的 schema、範例與變更紀錄。主要風險在於 `create_info_plist` 中對 `ext` 為空時的處理邏輯有誤，可能導致 panic 或產生無效的 plist；此外，`FileAssociation` 新增的欄位未提供預設值，可能造成反序列化錯誤。建議修正這些問題後再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷錯誤：`ext` 為空時仍會插入 `CFBundleTypeExtensions` | 0.95 |
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | `expect` 可能導致 panic：`name` 為 `None` 且 `ext` 為空時崩潰 | 0.90 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1185` | 新增欄位缺少 `#[serde(default)]`，可能導致反序列化錯誤 | 0.80 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1202` | 新增欄位缺少 `#[serde(default)]`，可能導致反序列化錯誤 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:271` | `exported_type` 的 `identifier` 未驗證唯一性 | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:291` | `UTTypeTagSpecification` 可能缺少必要的 key | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷錯誤：`ext` 為空時仍會插入 `CFBundleTypeExtensions`</summary>

在 `create_info_plist` 中，原本的邏輯是無論 `ext` 是否為空都會插入 `CFBundleTypeExtensions`。此 PR 試圖改為僅在 `ext` 非空時插入，但條件寫反了：`if association.ext.is_empty()` 會在 `ext` 為空時執行插入，導致空陣列被寫入 plist。這會產生無效的 `CFBundleTypeExtensions`，可能導致 macOS 無法正確註冊檔案關聯。

建議改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中新增的條件判斷為 `if association.ext.is_empty()`，但內部插入的內容是 `association.ext` 的陣列，邏輯矛盾。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> `expect` 可能導致 panic：`name` 為 `None` 且 `ext` 為空時崩潰</summary>

原本的程式碼使用 `unwrap_or(&association.ext[0].0)` 來提供預設名稱，但此 PR 改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空（例如僅使用 `contentTypes` 的關聯），程式將 panic。這違反了 [R16] 的錯誤處理原則，且可能導致打包流程中斷。

建議保留原本的 fallback 邏輯，或改用 `Result` 回傳錯誤。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect`，且未處理 `ext` 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1185</code> 新增欄位缺少 `#[serde(default)]`，可能導致反序列化錯誤</summary>

`FileAssociation` 新增了 `content_types` 和 `exported_type` 欄位，但未加上 `#[serde(default)]`。若使用者的 `tauri.conf.json` 中未提供這些欄位（舊版設定檔），反序列化時會因為缺少欄位而失敗。這會造成向後相容性問題。

建議為這兩個欄位加上 `#[serde(default)]`。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性，而其他可選欄位（如 `name`）有。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1202</code> 新增欄位缺少 `#[serde(default)]`，可能導致反序列化錯誤</summary>

`FileAssociation` 新增的 `exported_type` 欄位同樣缺少 `#[serde(default)]`。若設定檔中未提供此欄位，反序列化會失敗。

建議加上 `#[serde(default)]`。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:271</code> `exported_type` 的 `identifier` 未驗證唯一性</summary>

多個檔案關聯可能使用相同的 `exported_type.identifier`，這會導致 `UTExportedTypeDeclarations` 中出現重複的 `UTTypeIdentifier`，可能造成 macOS 的行為未定義。建議在產生 plist 前檢查 identifier 是否重複，或提供警告。

**判斷依據**：diff 中直接使用 `exported_type.identifier` 作為 key，未進行重複檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:291</code> `UTTypeTagSpecification` 可能缺少必要的 key</summary>

根據 Apple 文件，`UTTypeTagSpecification` 應至少包含 `public.filename-extension`、`public.mime-type` 或 `public.url-scheme` 之一。此處僅在 `mime_type` 存在時加入 `public.mime-type`，但若 `ext` 為空且 `mime_type` 也為空，則 `UTTypeTagSpecification` 會是空字典，可能導致類型無法被正確識別。建議在這種情況下跳過該 exported type 或提供警告。

**判斷依據**：diff 中 `specification` 的建立未檢查 `ext` 和 `mime_type` 是否同時為空。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8099 (cache hit 8064) ｜ completion tokens 1684 ｜ PR #12</sub>