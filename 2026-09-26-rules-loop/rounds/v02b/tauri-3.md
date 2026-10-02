<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 toml crate 從 0.8 升級至 0.9，並更新多個相依套件（toml_edit、serde、winnow 等）。主要風險在於 toml 0.9 的 API 變更可能導致編譯錯誤或行為差異，且 `do_parse_toml` 的錯誤處理被改為回傳 `ConfigError::FormatJson`，這會讓 TOML 解析錯誤被誤報為 JSON 格式錯誤，影響使用者診斷。此外，`BundleType` 新增 `Flatpak` 變體但未標記 `#[non_exhaustive]`，可能造成下游破壞性變更。建議先修正錯誤處理並確認所有相依套件相容性。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-utils/src/config/parse.rs:387` | TOML 解析錯誤被錯誤地包裝為 JSON 格式錯誤 | 0.95 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:147` | [R09] 公開 enum `BundleType` 新增變體但未標記 `#[non_exhaustive]` | 0.80 |
| ⚠️ | Major | `crates/tauri-cli/Cargo.toml:59` | toml_edit 升級至 0.23 可能引入不相容的 API 變更 | 0.70 |
| ⚠️ | Major | `crates/tauri-build/Cargo.toml:46` | toml 升級至 0.9 可能引入不相容的 API 變更 | 0.70 |
| ⚠️ | Major | `crates/tauri-plugin/Cargo.toml:38` | toml 升級至 0.9 可能引入不相容的 API 變更 | 0.70 |
| ⚠️ | Major | `crates/tauri-utils/Cargo.toml:37` | toml 升級至 0.9 可能引入不相容的 API 變更 | 0.70 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | `Display` 實作中 `Flatpak` 的大小寫不一致 | 0.70 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:209` | 反序列化接受 `"flatpak"` 但序列化輸出 `"Flatpak"`，可能造成 round-trip 失敗 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> TOML 解析錯誤被錯誤地包裝為 JSON 格式錯誤</summary>

在 `do_parse_toml` 中，原本將 `toml::from_str` 的錯誤包裝為 `ConfigError::FormatToml`，但此 PR 改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會導致 TOML 解析失敗時，使用者看到的是 JSON 格式錯誤訊息，造成誤導。應保留 `ConfigError::FormatToml` 變體，或新增專屬的 TOML 錯誤變體。

**判斷依據**：diff 中 `do_parse_toml` 的錯誤處理從 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，且錯誤型別從 `toml::de::Error` 改為 `serde_json::Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:147</code> [R09] 公開 enum `BundleType` 新增變體但未標記 `#[non_exhaustive]`</summary>

`BundleType` 是公開 enum，新增 `Flatpak` 變體可能導致下游 match 不完整而編譯失敗。根據規範 R09，公開錯誤 enum 應標記 `#[non_exhaustive]` 以保留未來擴充彈性。建議在 enum 定義加上 `#[non_exhaustive]`。

**判斷依據**：diff 新增 `Flatpak` 變體，但 enum 定義沒有 `#[non_exhaustive]` 屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/Cargo.toml:59</code> toml_edit 升級至 0.23 可能引入不相容的 API 變更</summary>

`toml_edit` 從 0.22 升級至 0.23，這是一個 major 版本升級，可能包含 breaking changes。需要確認程式碼中使用的 API 是否仍然相容，否則可能導致編譯失敗。建議檢查 `toml_edit` 的 changelog 並更新相關程式碼。

**判斷依據**：diff 中 `toml_edit` 版本從 0.22 改為 0.23。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-build/Cargo.toml:46</code> toml 升級至 0.9 可能引入不相容的 API 變更</summary>

`toml` 從 0.8 升級至 0.9，這是 major 版本升級，可能包含 breaking changes。需要確認程式碼中使用的 API 是否仍然相容，否則可能導致編譯失敗。建議檢查 `toml` 的 changelog 並更新相關程式碼。

**判斷依據**：diff 中 `toml` 版本從 0.8 改為 0.9。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-plugin/Cargo.toml:38</code> toml 升級至 0.9 可能引入不相容的 API 變更</summary>

`toml` 從 0.8 升級至 0.9，這是 major 版本升級，可能包含 breaking changes。需要確認程式碼中使用的 API 是否仍然相容，否則可能導致編譯失敗。建議檢查 `toml` 的 changelog 並更新相關程式碼。

**判斷依據**：diff 中 `toml` 版本從 0.8 改為 0.9。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/Cargo.toml:37</code> toml 升級至 0.9 可能引入不相容的 API 變更</summary>

`toml` 從 0.8 升級至 0.9，這是 major 版本升級，可能包含 breaking changes。需要確認程式碼中使用的 API 是否仍然相容，否則可能導致編譯失敗。建議檢查 `toml` 的 changelog 並更新相關程式碼。

**判斷依據**：diff 中 `toml` 版本從 0.8 改為 0.9。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> `Display` 實作中 `Flatpak` 的大小寫不一致</summary>

`Display` 實作中，`Flatpak` 回傳 `"Flatpak"`（首字母大寫），但其他變體如 `Nsis` 回傳 `"nsis"`、`Dmg` 回傳 `"dmg"`。這可能導致序列化輸出不統一，影響設定檔或日誌的可讀性。建議改為 `"flatpak"` 以維持一致性。

**判斷依據**：diff 中 `Display` 實作新增 `Self::Flatpak => "Flatpak"`，與其他變體的小寫形式不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:209</code> 反序列化接受 `"flatpak"` 但序列化輸出 `"Flatpak"`，可能造成 round-trip 失敗</summary>

`Deserialize` 實作接受 `"flatpak"`，但 `Display` 輸出 `"Flatpak"`。若程式依賴 `Display` 進行序列化，則反序列化時可能無法解析自己輸出的字串。建議統一大小寫。

**判斷依據**：diff 中 `Deserialize` 新增 `"flatpak"` 分支，但 `Display` 輸出 `"Flatpak"`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8464 (cache hit 8448) ｜ completion tokens 1999 ｜ PR #3</sub>