<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 檔案關聯新增了 contentTypes 與 exportedType 支援，並更新了對應的 schema、範例與變更日誌。主要風險在於 `create_info_plist` 中對 `CFBundleTypeExtensions` 的條件判斷可能顛倒，導致有副檔名的關聯無法正確設定；此外，`CFBundleTypeName` 改用 `expect` 可能在建置時 panic。整體方向正確，但需修正上述問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | CFBundleTypeExtensions 條件判斷相反 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:340` | CFBundleTypeName 使用 expect 可能導致 panic | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> CFBundleTypeExtensions 條件判斷相反</summary>

在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（即一般情況），`CFBundleTypeExtensions` 不會被加入 plist，使得 macOS 無法將檔案副檔名與應用程式關聯。應改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中新增的條件判斷 `if association.ext.is_empty()` 與原本的無條件插入形成對比，且語意上應為「有副檔名才插入」。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:340</code> CFBundleTypeName 使用 expect 可能導致 panic</summary>

原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未設定 `name` 且 `ext` 為空（例如僅使用 contentTypes 的關聯），則會在建置時 panic。建議保留原本的 fallback 邏輯，或提供更明確的錯誤處理。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect`，且 `name` 為 `Option<String>`，未處理 `None` 情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6053 (cache hit 6016) ｜ completion tokens 711 ｜ PR #12</sub>