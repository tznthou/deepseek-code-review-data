<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 檔案關聯新增了 `content_types` 與 `exported_type` 支援，並更新了對應的 schema、範例與變更日誌。主要風險在於 `create_info_plist` 中對 `ext` 為空時的處理邏輯有誤，可能導致 panic 或產生無效的 plist；此外，`CFBundleTypeExtensions` 的條件判斷似乎顛倒了，會讓有副檔名的關聯遺失該欄位。建議先修正這些正確性問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷顛倒：有副檔名時反而跳過 CFBundleTypeExtensions | 0.95 |
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic：當 name 與 ext 皆為空時 | 0.90 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1185` | 新增欄位未加上 serde(default)，可能破壞既有設定檔相容性 | 0.80 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1202` | 新增欄位未加上 serde(default)，可能破壞既有設定檔相容性 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:271` | UTExportedTypeDeclarations 的 identifier 可能重複或無效 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷顛倒：有副檔名時反而跳過 CFBundleTypeExtensions</summary>

在 `create_info_plist` 中，原本的程式碼會為每個 association 建立 `CFBundleTypeExtensions` 陣列。修改後，此區塊被包在 `if association.ext.is_empty()` 內，這表示只有當 `ext` 為空時才會加入 `CFBundleTypeExtensions`，但空陣列本身沒有意義；而當 `ext` 有值時（正常情況），反而會遺漏此必要欄位。這會導致 macOS 無法正確將檔案類型與應用程式關聯。

建議改為 `if !association.ext.is_empty()`，或直接移除條件判斷，恢復原本的邏輯。

**判斷依據**：diff 中新增的 `if association.ext.is_empty()` 包住了原本的 `CFBundleTypeExtensions` 插入邏輯，而原本的程式碼是無條件插入。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic：當 name 與 ext 皆為空時</summary>

原本的程式碼使用 `unwrap_or(&association.ext[0].0)` 來提供預設名稱，但修改後改為 `expect("File association must have a name")`。這表示如果使用者未提供 `name` 且 `ext` 為空（例如只使用 `content_types` 的關聯），程式會在打包時 panic。

建議保留原本的 fallback 邏輯，或改為在驗證階段就確保 `name` 或 `ext` 至少存在一個，並提供明確的錯誤訊息。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect(...)`，且 `ext` 可能為空（因為新增了 `content_types` 欄位，允許只透過 content type 關聯）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1185</code> 新增欄位未加上 serde(default)，可能破壞既有設定檔相容性</summary>

`FileAssociation` 新增了 `content_types` 與 `exported_type` 欄位，但沒有加上 `#[serde(default)]`。這表示既有的 `tauri.conf.json` 若未包含這些欄位，反序列化時會失敗，造成 breaking change。

建議為這兩個欄位加上 `#[serde(default)]`，以維持向後相容。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性，而其他選用欄位（如 `name`）也沒有，但此處為新增欄位，會影響既有設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1202</code> 新增欄位未加上 serde(default)，可能破壞既有設定檔相容性</summary>

`FileAssociation` 新增的 `exported_type` 欄位同樣缺少 `#[serde(default)]`，會導致既有設定檔在反序列化時失敗。

建議加上 `#[serde(default)]`。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:271</code> UTExportedTypeDeclarations 的 identifier 可能重複或無效</summary>

`exported_type.identifier` 直接插入 `UTTypeIdentifier`，但沒有驗證其唯一性或格式。若多個 association 使用相同的 identifier，或 identifier 不符合 UTI 規範（例如包含非法字元），可能導致 macOS 無法正確處理。

建議在設定驗證階段檢查 identifier 的唯一性與格式。

**判斷依據**：diff 中直接使用 `exported_type.identifier`，沒有額外檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8171 (cache hit 1536) ｜ completion tokens 1408 ｜ PR #12</sub>