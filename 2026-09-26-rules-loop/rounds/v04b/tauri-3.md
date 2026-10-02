<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml 依賴從 0.8 升級到 0.9，並更新相關 crate（toml_edit、serde、winnow 等）。同時在 BundleType 枚舉中新增 Flatpak 變體。主要風險在於 toml 0.9 的 API 變更可能導致編譯錯誤或行為差異，且 config.rs 中新增的 Flatpak 變體可能影響序列化與反序列化相容性。此外，parse.rs 中的錯誤處理將 TOML 錯誤映射為 JSON 錯誤，可能遺失錯誤類型資訊。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | TOML 解析錯誤被錯誤地映射為 JSON 錯誤 | 0.80 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:147` | 新增 Flatpak 變體可能破壞向後相容性 | 0.70 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | Display 實作中 Flatpak 的大小寫不一致 | 0.60 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:209` | 反序列化接受 "flatpak" 但 Display 輸出 "Flatpak"，可能造成不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> TOML 解析錯誤被錯誤地映射為 JSON 錯誤</summary>

在 `do_parse_toml` 函數中，將 `toml::from_str` 的錯誤映射為 `ConfigError::FormatJson`，這會導致錯誤類型不正確，可能誤導使用者。應使用 `ConfigError::FormatToml` 並保留原始錯誤。

**判斷依據**：diff 中顯示原本使用 `ConfigError::FormatToml`，但被改為 `ConfigError::FormatJson`，且錯誤被轉換為 `serde_json::Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 Flatpak 變體可能破壞向後相容性</summary>

在 `BundleType` 枚舉中新增 `Flatpak` 變體，但未標記 `#[non_exhaustive]`，這可能導致下游程式碼在匹配時出現非窮盡匹配錯誤。若此枚舉為公開 API，應考慮標記為 `#[non_exhaustive]` 或提供其他相容性措施。

**判斷依據**：diff 中新增了 `Flatpak` 變體，但未見 `#[non_exhaustive]` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> Display 實作中 Flatpak 的大小寫不一致</summary>

在 `Display` 實作中，`Flatpak` 被輸出為 "Flatpak"（首字母大寫），而其他變體如 "nsis"、"app"、"dmg" 均為小寫。這可能導致序列化後的字串與反序列化期望不一致（反序列化接受 "flatpak"）。建議統一為小寫 "flatpak"。

**判斷依據**：diff 中顯示 `Self::Flatpak => "Flatpak"`，而其他變體均為小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:209</code> 反序列化接受 "flatpak" 但 Display 輸出 "Flatpak"，可能造成不一致</summary>

在 `Deserialize` 實作中，接受 "flatpak"（小寫），但 `Display` 輸出 "Flatpak"（首字母大寫）。這可能導致序列化後再反序列化失敗，或與其他工具鏈的預期不一致。建議統一大小寫。

**判斷依據**：diff 中顯示反序列化接受 "flatpak"，而 Display 輸出 "Flatpak"。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7437 (cache hit 7424) ｜ completion tokens 1004 ｜ PR #3</sub>