<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 toml crate 從 0.8 升級至 0.9，並連帶更新多個相依套件（如 serde、toml_edit、winnow 等）。同時新增了 Flatpak bundle type 的支援。主要風險在於 toml 0.9 的 API 變更可能導致解析錯誤處理不正確，以及新增的 Flatpak 變體在 Display 實作中大小寫不一致，可能造成序列化或比對問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤類型從 FormatToml 改為 FormatJson，導致 TOML 解析錯誤被誤報為 JSON 錯誤 | 0.95 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:180` | Flatpak 的 Display 實作大小寫不一致 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤類型從 FormatToml 改為 FormatJson，導致 TOML 解析錯誤被誤報為 JSON 錯誤</summary>

在 `do_parse_toml` 函式中，原本將 `toml::from_str` 的錯誤包裝為 `ConfigError::FormatToml`，但升級後改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會讓 TOML 解析失敗時回報為 JSON 格式錯誤，誤導使用者。應保留 `FormatToml` 變體，或新增對應的錯誤類型。

**判斷依據**：diff 中顯示原本的 `ConfigError::FormatToml` 被改為 `ConfigError::FormatJson`，且錯誤被轉為 `serde_json::Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:180</code> Flatpak 的 Display 實作大小寫不一致</summary>

在 `Display for BundleType` 中，其他變體都輸出小寫（如 "deb"、"rpm"），但新增的 `Flatpak` 輸出 "Flatpak"（首字母大寫）。這可能導致序列化或比對時出現不一致，例如在產生 bundle 檔名或與其他工具互動時。建議改為 "flatpak"。

**判斷依據**：diff 中新增的 match arm 為 `Self::Flatpak => "Flatpak"`，而其他 arm 皆為小寫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6819 (cache hit 1536) ｜ completion tokens 638 ｜ PR #3</sub>