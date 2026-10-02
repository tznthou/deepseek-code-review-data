<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了 content types 與 exported type 支援，並更新了 schema、範例與變更日誌。主要風險在於 `create_info_plist` 中對 `CFBundleTypeExtensions` 的條件判斷邏輯可能相反，導致有副檔名的關聯反而缺少必要的 key；此外 `CFBundleTypeName` 改用 `expect` 可能造成 panic。整體功能方向正確，但需修正上述問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | CFBundleTypeExtensions 條件判斷邏輯相反 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/macos/app.rs:353` | 使用 expect 可能導致 panic | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:1184` | content_types 欄位缺少 serde default | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> CFBundleTypeExtensions 條件判斷邏輯相反</summary>

在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（即一般情況），該 key 不會被加入，使得 macOS 無法正確關聯副檔名。應改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中原本的 `dict.insert("CFBundleTypeExtensions", ...)` 被包在 `if association.ext.is_empty()` 內，但邏輯上應該只在 ext 非空時才需要此 key。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:353</code> 使用 expect 可能導致 panic</summary>

原本 `name` 為 None 時會 fallback 到 `ext[0]`，現在改用 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空（例如僅使用 content types 的關聯），程式會 panic。建議保留原本的 fallback 邏輯或提供更安全的處理。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect`，但未考慮 `ext` 可能為空的情境。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:1184</code> content_types 欄位缺少 serde default</summary>

新增的 `content_types` 欄位型別為 `Option<Vec<String>>`，但未加上 `#[serde(default)]`。若使用者的設定檔中未提供此欄位，反序列化時會失敗。建議加上 `#[serde(default)]` 以維持向後相容。

**判斷依據**：其他選用欄位如 `name` 有 `Option` 且未加 default 也能運作，但此處為新增欄位，舊設定檔可能未包含，需確認 serde 對 Option 的預設行為。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6089 (cache hit 6016) ｜ completion tokens 872 ｜ PR #12</sub>