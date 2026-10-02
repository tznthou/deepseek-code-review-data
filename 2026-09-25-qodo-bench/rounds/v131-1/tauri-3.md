<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 Rust crate 依賴（toml 0.8→0.9、toml_edit 0.22→0.23 等），並在 BundleType 枚舉中新增 Flatpak 變體。主要風險在於 toml 0.9 的 API 變更可能導致解析錯誤處理不當，以及新增的 Flatpak 變體在 Display 實作中大小寫不一致。建議修正錯誤處理並統一命名。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | TOML 解析錯誤被錯誤地包裝為 JSON 錯誤 | 0.90 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | Flatpak 的 Display 實作大小寫不一致 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> TOML 解析錯誤被錯誤地包裝為 JSON 錯誤</summary>

在 `do_parse_toml` 函數中，原本使用 `ConfigError::FormatToml` 來包裝 TOML 解析錯誤，但更新後改為使用 `ConfigError::FormatJson`，並將錯誤轉換為 `serde_json::Error`。這會導致錯誤類型不匹配，可能使呼叫端無法正確處理 TOML 格式錯誤，且錯誤訊息可能誤導使用者。建議保留 `ConfigError::FormatToml` 變體，或新增一個專門的 TOML 錯誤變體。

**判斷依據**：diff 中將 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，並使用 `serde_json::Error::custom` 包裝錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> Flatpak 的 Display 實作大小寫不一致</summary>

在 `Display for BundleType` 的實作中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體如 `Nsis`、`App`、`Dmg` 都回傳小寫字串。這可能導致序列化或顯示時的不一致，建議改為 `"flatpak"` 以維持一致性。

**判斷依據**：diff 中新增的 `Display` 分支回傳 `"Flatpak"`，而其他分支回傳小寫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6346 (cache hit 1408) ｜ completion tokens 637 ｜ PR #3</sub>