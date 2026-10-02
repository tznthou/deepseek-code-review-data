<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml crate 從 0.8 升級到 0.9，並更新相關依賴（toml_edit、serde、winnow 等），同時新增 BundleType::Flatpak 變體。主要風險在於 toml 0.9 的 API 變更可能導致編譯錯誤或行為差異，且 config.rs 中新增的 Flatpak 變體可能影響序列化與反序列化相容性。此外，do_parse_toml 的錯誤處理改為使用 ConfigError::FormatJson 可能造成錯誤類型混淆。建議先確認所有使用 toml 的程式碼已適應新版本，並補充測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤類型不匹配：使用 ConfigError::FormatJson 包裝 TOML 解析錯誤 | 0.80 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 可能破壞既有序列化/反序列化 | 0.70 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 未更新所有相關 match 或測試 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/Cargo.toml:59` | toml_edit 升級到 0.23 可能導致 API 不相容 | 0.50 |
| 🔸 | Minor | `crates/tauri-build/Cargo.toml:46` | toml 升級到 0.9 可能導致 API 不相容 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤類型不匹配：使用 ConfigError::FormatJson 包裝 TOML 解析錯誤</summary>

在 `do_parse_toml` 中，原本使用 `ConfigError::FormatToml` 來包裝 TOML 解析錯誤，但現在改為 `ConfigError::FormatJson`，這會導致錯誤類型與實際格式不符，可能誤導使用者或呼叫端。建議保留 `ConfigError::FormatToml` 變體，或新增專用的 TOML 錯誤變體。

**判斷依據**：diff 中顯示原本的 `ConfigError::FormatToml` 被替換為 `ConfigError::FormatJson`，且錯誤被轉換為 `serde_json::Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 可能破壞既有序列化/反序列化</summary>

新增 `BundleType::Flatpak` 變體後，`Display` 實作回傳 "Flatpak"（大寫 F），但 `Deserialize` 接受 "flatpak"（小寫）。這可能導致序列化後的字串無法被反序列化（例如使用 serde 序列化為 "Flatpak" 後，反序列化時會因大小寫不符而失敗）。建議統一大小寫，或使用 `#[serde(rename_all = "lowercase")]` 等屬性。

**判斷依據**：diff 中新增 `Flatpak` 變體，且 `Display` 回傳 "Flatpak"，但 `Deserialize` 接受 "flatpak"。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 未更新所有相關 match 或測試</summary>

新增 enum 變體後，可能需要在其他 match 或測試中處理新變體，否則可能導致編譯錯誤或未覆蓋的行為。請確認所有使用 `BundleType` 的地方都已更新。

**判斷依據**：diff 中新增變體，但未顯示其他檔案的相應修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/Cargo.toml:59</code> toml_edit 升級到 0.23 可能導致 API 不相容</summary>

`toml_edit` 從 0.22 升級到 0.23，可能包含 breaking changes。請確認程式碼中使用的 API 仍然相容，或已做相應調整。

**判斷依據**：diff 中將 toml_edit 版本從 0.22 改為 0.23。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-build/Cargo.toml:46</code> toml 升級到 0.9 可能導致 API 不相容</summary>

`toml` crate 從 0.8 升級到 0.9，可能包含 breaking changes。請確認程式碼中使用的 API 仍然相容，或已做相應調整。

**判斷依據**：diff 中將 toml 版本從 0.8 改為 0.9。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8474 (cache hit 8448) ｜ completion tokens 1221 ｜ PR #3</sub>