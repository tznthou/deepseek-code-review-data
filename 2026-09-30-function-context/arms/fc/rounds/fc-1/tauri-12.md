<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 支援，並更新了對應的 schema 與範例。主要風險在於 `create_info_plist` 中對 `name` 欄位的處理：原本有 fallback 到 `ext[0]`，現在改為 `expect`，若使用者未提供 `name` 且 `ext` 為空，將導致 panic。此外，`CFBundleTypeExtensions` 的條件判斷邏輯可能相反，導致有副檔名時反而未寫入。建議修正這些邏輯並補充測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | `expect` 取代 fallback 可能導致 panic | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | `CFBundleTypeExtensions` 條件判斷可能相反 | 0.85 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1185` | 新增欄位未加上 `#[serde(default)]` | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> `expect` 取代 fallback 可能導致 panic</summary>

原本的程式碼在 `name` 為 `None` 時會 fallback 到 `association.ext[0].0`，但現在改為 `expect("File association must have a name")`。如果使用者未提供 `name` 且 `ext` 為空（或 `ext` 的第一個元素不存在），程式會 panic。這會讓建置流程直接崩潰，且錯誤訊息不夠明確。

建議：保留原本的 fallback 邏輯，或改用更安全的處理方式，例如在 `ext` 為空時使用預設名稱或回傳錯誤。

**判斷依據**：diff 中原本的 `unwrap_or(&association.ext[0].0)` 被替換為 `expect`，且 `ext` 欄位型別為 `Vec<AssociationExt>`，可能為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> `CFBundleTypeExtensions` 條件判斷可能相反</summary>

程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，但這與預期相反：通常應該在有副檔名時才加入此鍵。若 `ext` 為空，則不應加入；若 `ext` 非空，則應加入。目前的寫法會導致有副檔名時反而沒有寫入 `CFBundleTypeExtensions`，可能影響檔案關聯功能。

建議：將條件改為 `!association.ext.is_empty()`。

**判斷依據**：diff 中新增了 `if association.ext.is_empty()` 條件，但原本的程式碼是無條件插入 `CFBundleTypeExtensions`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1185</code> 新增欄位未加上 `#[serde(default)]`</summary>

`content_types` 和 `exported_type` 欄位沒有加上 `#[serde(default)]`，這表示在反序列化時如果 JSON 中缺少這些欄位，會導致錯誤。雖然 `Option` 型別通常會自動處理缺失欄位，但加上 `#[serde(default)]` 可以更明確地表達意圖，並避免未來若欄位型別變更時出現問題。

建議：為這兩個欄位加上 `#[serde(default)]`。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性，而其他欄位如 `role` 和 `rank` 都有。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8864 (cache hit 1536) ｜ completion tokens 999 ｜ PR #12</sub>