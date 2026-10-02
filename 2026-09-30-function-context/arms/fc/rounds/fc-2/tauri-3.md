<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 TOML 相關依賴從 0.8 升級至 0.9，並新增 Flatpak bundle 類型。升級本身風險較低，但 `do_parse_toml` 的錯誤處理被改為回報 `FormatJson`，導致錯誤類型不正確，可能誤導使用者。此外，`BundleType::Flatpak` 的 `Display` 實作輸出「Flatpak」而非「flatpak」，與其他 variant 的小寫慣例不一致，可能造成序列化或比對問題。建議修正錯誤處理並統一顯示格式。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | TOML 解析錯誤被錯誤地回報為 JSON 格式錯誤 | 0.90 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | BundleType::Flatpak 的 Display 輸出大小寫不一致 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> TOML 解析錯誤被錯誤地回報為 JSON 格式錯誤</summary>

在 `do_parse_toml` 中，原本將 `toml::from_str` 的錯誤包裝為 `ConfigError::FormatToml`，但此 PR 改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會導致當 TOML 檔案格式錯誤時，使用者看到的錯誤訊息會指向 JSON 格式問題，造成混淆。建議保留 `FormatToml` variant，或新增專屬的 TOML 錯誤 variant，並直接傳遞原始錯誤。

**判斷依據**：diff 中將原本的 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，且錯誤被轉為 `serde_json::Error`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> BundleType::Flatpak 的 Display 輸出大小寫不一致</summary>

`Display` 實作中，`Flatpak` 輸出為「Flatpak」，但其他 variant 皆為小寫（如「deb」、「rpm」）。這可能導致依賴 `to_string()` 進行比對或序列化時出現不一致。建議改為「flatpak」以維持一致性。

**判斷依據**：diff 中新增的 `Display` 分支回傳 "Flatpak"，而其他分支皆為小寫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6819 (cache hit 6784) ｜ completion tokens 640 ｜ PR #3</sub>