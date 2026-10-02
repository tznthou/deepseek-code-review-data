<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml crate 從 0.8 升級到 0.9，並更新相關依賴（toml_edit、serde、winnow 等），同時在 BundleType 枚舉中新增 Flatpak 變體。升級可能引入 API 變更，需確認程式碼相容性；新增的 Flatpak 變體需要更新對應的序列化/反序列化邏輯與文件。此外，do_parse_toml 的錯誤處理改為使用 ConfigError::FormatJson，可能導致錯誤類型不匹配。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤處理不當：使用 FormatJson 包裝 TOML 解析錯誤 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | [R07] 新增的 BundleType::Flatpak 缺少文件註解 | 0.70 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | BundleType 的 Display 實作中 Flatpak 大小寫不一致 | 0.60 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:209` | BundleType 的 Deserialize 實作中缺少對 "Flatpak" 的處理 | 0.50 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 可能影響既有程式碼的 exhaustive match | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤處理不當：使用 FormatJson 包裝 TOML 解析錯誤</summary>

在 `do_parse_toml` 中，將 `toml::from_str` 的錯誤映射為 `ConfigError::FormatJson`，這可能導致錯誤類型不匹配，使呼叫端無法正確處理 TOML 格式錯誤。建議新增一個 `FormatToml` 變體來包裝 TOML 錯誤，或使用更通用的錯誤類型。

**判斷依據**：diff 中顯示原本使用 `ConfigError::FormatToml`，但被改為 `ConfigError::FormatJson`，且將 TOML 錯誤轉為字串後再包裝成 `serde_json::Error`，這可能導致錯誤資訊丟失或類型不符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> [R07] 新增的 BundleType::Flatpak 缺少文件註解</summary>

新增的 `Flatpak` 變體沒有文件註解，違反了專案規範 R07（Public APIs Must Include Documentation Comments）。建議為該變體添加說明其用途的文件註解。

**判斷依據**：diff 中新增了 `Flatpak` 變體，但沒有文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> BundleType 的 Display 實作中 Flatpak 大小寫不一致</summary>

在 `Display` 實作中，`Flatpak` 被輸出為 "Flatpak"（首字母大寫），而其他變體均為小寫（如 "nsis"、"app"）。這可能導致序列化後的字串與反序列化期望不一致，建議統一為小寫 "flatpak"。

**判斷依據**：diff 中新增的 `Display` 分支使用了 "Flatpak"，而其他分支均為小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:209</code> BundleType 的 Deserialize 實作中缺少對 "Flatpak" 的處理</summary>

在 `Deserialize` 實作中，僅處理了小寫 "flatpak"，但 `Display` 輸出的是 "Flatpak"，這可能導致序列化後的字串無法被反序列化。建議統一大小寫，或在反序列化時同時接受兩種形式。

**判斷依據**：diff 中新增的反序列化分支僅匹配 "flatpak"，而 `Display` 輸出 "Flatpak"。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 可能影響既有程式碼的 exhaustive match</summary>

新增 `Flatpak` 變體可能導致其他 crate 中對 `BundleType` 的 exhaustive match 出現編譯錯誤，需要檢查並更新所有相關 match 分支。

**判斷依據**：diff 中新增了 `Flatpak` 變體，但未提供其他 match 的更新。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8392 (cache hit 8320) ｜ completion tokens 1148 ｜ PR #3</sub>