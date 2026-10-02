<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 的支援，並更新了設定結構與範例。主要風險在於 `create_info_plist` 中對 `ext` 為空時的處理邏輯有誤，可能導致 `CFBundleTypeExtensions` 未被加入；此外，`CFBundleTypeName` 改用 `expect` 可能造成 panic。整體功能方向正確，但需修正上述問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷錯誤：ext 為空時才加入 CFBundleTypeExtensions | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.85 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1184` | content_types 欄位缺少 serde 別名 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷錯誤：ext 為空時才加入 CFBundleTypeExtensions</summary>

在 `create_info_plist` 中，原本的程式碼無條件加入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty()` 才加入。這會導致當 `ext` 非空時（正常情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，造成檔案關聯失效。

**失敗情境**：使用者設定 `ext: ["png"]`，產生的 Info.plist 將缺少 `CFBundleTypeExtensions`，macOS 無法將 .png 檔案與應用程式關聯。

**建議**：移除 `if association.ext.is_empty()` 條件，改回無條件加入，或改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中新增的 `if association.ext.is_empty()` 條件包住了原本無條件的 `CFBundleTypeExtensions` 插入，邏輯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，修改後改為 `expect("File association must have a name")`。若使用者未設定 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定檔中某個 file association 未提供 `name` 且 `ext` 為空陣列，打包時會 panic 並中止。

**建議**：保留原本的 fallback 邏輯，或改用更安全的錯誤處理（例如回傳錯誤而非 panic）。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect`，移除了 fallback。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1184</code> content_types 欄位缺少 serde 別名</summary>

新增的 `content_types` 欄位使用了 `#[serde(alias = "content-types")]`，但 JSON schema 中定義的屬性名稱為 `contentTypes`（camelCase）。若使用者依照 schema 使用 `contentTypes`，反序列化時可能無法正確對應。

**失敗情境**：設定檔中使用 `contentTypes` 屬性，但 Rust 結構體期望 `content_types` 或 `content-types`，導致欄位被忽略。

**建議**：確認 serde 的命名策略，或同時支援 `contentTypes` 別名。

**判斷依據**：diff 中新增的欄位僅有 `content-types` 別名，但 schema 使用 `contentTypes`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6053 (cache hit 1408) ｜ completion tokens 1013 ｜ PR #12</sub>