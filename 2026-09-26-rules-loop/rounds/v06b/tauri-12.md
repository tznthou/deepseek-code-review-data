<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 macOS 的檔案關聯新增了自訂型別支援（UTExportedTypeDeclarations 與 LSItemContentTypes），並更新了設定結構、schema 與範例。主要風險在於 `create_info_plist` 中對 `association.ext` 為空時的處理邏輯有誤，可能導致 panic 或產生無效的 plist；此外，`FileAssociation` 新增的 `content_types` 欄位未設定 `#[serde(default)]`，可能造成向後相容性問題。建議先修正這些問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:328` | 條件判斷錯誤：`association.ext.is_empty()` 應為 `!association.ext.is_empty()` | 0.95 |
| 🛑 | Blocker | `crates/tauri-bundler/src/bundle/macos/app.rs:340` | `expect` 可能導致 panic：`association.name` 為 None 且 `ext` 為空時 | 0.90 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:1184` | 缺少 `#[serde(default)]` 可能導致向後相容性問題 | 0.85 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/macos/app.rs:271` | `UTTypeTagSpecification` 可能缺少必要的 `public.filename-extension` | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:328</code> 條件判斷錯誤：`association.ext.is_empty()` 應為 `!association.ext.is_empty()`</summary>

在 `create_info_plist` 中，原本的程式碼會將 `CFBundleTypeExtensions` 設定為 `association.ext` 的內容。此 PR 將其包在 `if association.ext.is_empty()` 條件內，但這會導致只有當 `ext` 為空時才加入該鍵，與預期相反。

**失敗情境**：當 `ext` 非空時（例如 `["png"]`），`CFBundleTypeExtensions` 不會被加入 plist，導致 macOS 無法將檔案類型與應用程式關聯。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

**判斷依據**：diff 中新增的 `if association.ext.is_empty()` 條件與原本無條件插入的程式碼形成對比，且後續 `CFBundleTypeName` 使用 `expect` 假設 `ext` 非空，邏輯矛盾。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:340</code> `expect` 可能導致 panic：`association.name` 為 None 且 `ext` 為空時</summary>

原本的程式碼使用 `unwrap_or(&association.ext[0].0)` 來提供預設名稱，但此 PR 改為 `expect("File association must have a name")`。若 `association.name` 為 `None` 且 `association.ext` 為空，則會 panic。

**失敗情境**：使用者設定了一個沒有 `name` 且 `ext` 為空的 file association（例如僅使用 `contentTypes` 來關聯既有型別），打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改為在 `ext` 為空時使用其他預設值（如 `"File"`），或直接省略 `CFBundleTypeName`。

**判斷依據**：diff 中將 `unwrap_or(&association.ext[0].0)` 改為 `expect`，且未處理 `ext` 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:1184</code> 缺少 `#[serde(default)]` 可能導致向後相容性問題</summary>

新增的 `content_types` 欄位沒有加上 `#[serde(default)]`。若使用者的 `tauri.conf.json` 是舊版格式，沒有此欄位，反序列化時會失敗。

**失敗情境**：現有使用者的設定檔中沒有 `contentTypes` 欄位，升級後執行 `tauri build` 會因缺少欄位而報錯。

**建議修法**：在欄位上加上 `#[serde(default)]`，使其在缺失時預設為 `None`。

**判斷依據**：diff 中新增的欄位沒有 `#[serde(default)]`，而其他可選欄位（如 `name`）都有。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/macos/app.rs:271</code> `UTTypeTagSpecification` 可能缺少必要的 `public.filename-extension`</summary>

在建立 `UTExportedTypeDeclarations` 時，`UTTypeTagSpecification` 中的 `public.filename-extension` 是從 `association.ext` 取得。若 `association.ext` 為空，則會產生一個空的陣列，可能導致 macOS 無法正確識別此型別。

**失敗情境**：使用者定義了一個 exported type 但沒有指定任何副檔名（僅透過 `contentTypes` 關聯），則產生的 plist 中 `public.filename-extension` 為空陣列，可能導致型別無法被系統使用。

**建議修法**：若 `ext` 為空，考慮省略 `public.filename-extension` 或提供其他標籤。

**判斷依據**：diff 中直接使用 `association.ext` 建立陣列，未檢查是否為空。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8161 (cache hit 8064) ｜ completion tokens 1509 ｜ PR #12</sub>