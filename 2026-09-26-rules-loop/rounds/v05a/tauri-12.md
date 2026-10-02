<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 檔案關聯新增了自訂型別（UTExportedTypeDeclarations）與內容型別（LSItemContentTypes）的支援，並更新了設定結構與範例。主要風險在於 `create_info_plist` 中對 `association.ext` 為空時的處理邏輯可能導致 `CFBundleTypeExtensions` 被錯誤省略，以及 `expect` 的使用可能造成 panic。此外，新增的 `ExportedFileAssociation` 結構體缺少 `#[non_exhaustive]` 屬性，可能影響 API 穩定性。建議修正這些問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷反了：ext 為空時反而插入 CFBundleTypeExtensions | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1209` | [R09] ExportedFileAssociation 應標記為 non_exhaustive | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷反了：ext 為空時反而插入 CFBundleTypeExtensions</summary>

在 `create_info_plist` 中，原本的邏輯是無論 `ext` 是否為空都會插入 `CFBundleTypeExtensions`。修改後變成 `if association.ext.is_empty()` 才插入，這與預期相反：當 `ext` 為空時，不應該有 `CFBundleTypeExtensions`，但現在卻會插入一個空陣列；而當 `ext` 非空時，反而會遺漏該鍵。這會導致 macOS 無法正確關聯檔案類型。

建議改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中原本的 `dict.insert("CFBundleTypeExtensions", ...)` 被包在 `if association.ext.is_empty()` 內，但條件應為非空才插入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

原本使用 `unwrap_or(&association.ext[0].0)` 提供預設名稱，現在改為 `expect("File association must have a name")`。如果 `name` 為 `None` 且 `ext` 為空（例如使用者只設定 `contentTypes` 而沒有 `ext`），程式會 panic。建議改回使用 `unwrap_or` 或提供更安全的預設值。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect`，但 `ext` 可能為空，導致 panic。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1209</code> [R09] ExportedFileAssociation 應標記為 non_exhaustive</summary>

新增的公開結構體 `ExportedFileAssociation` 未來可能需要增加欄位，建議加上 `#[non_exhaustive]` 以避免破壞性變更。

**判斷依據**：diff 中新增的結構體未加上 `#[non_exhaustive]`，違反專案規範 R09。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8099 (cache hit 6016) ｜ completion tokens 884 ｜ PR #12</sub>