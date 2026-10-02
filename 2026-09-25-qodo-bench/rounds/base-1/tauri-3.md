<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml crate 從 0.8 升級至 0.9，並更新相關依賴（toml_edit、serde、winnow 等），同時新增 Flatpak bundle type。主要風險在於 toml 0.9 的 API 變更可能導致解析錯誤處理不當，以及新增的 Flatpak 變體在 Display 實作中大小寫不一致。建議修正錯誤處理並確認 Flatpak 的序列化行為。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | TOML 解析錯誤被錯誤地包裝為 JSON 格式錯誤 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | Flatpak 的 Display 實作大小寫不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> TOML 解析錯誤被錯誤地包裝為 JSON 格式錯誤</summary>

在 `do_parse_toml` 中，原本使用 `ConfigError::FormatToml` 來包裝 TOML 解析錯誤，但升級後改為使用 `ConfigError::FormatJson`，並將錯誤轉為字串後包裝成 `serde_json::Error`。這會導致錯誤類型不正確，使用者將看到誤導的錯誤訊息（例如「JSON 格式錯誤」而非「TOML 格式錯誤」），且可能丟失錯誤的結構化資訊（如行號、欄位）。建議保留 `ConfigError::FormatToml` 變體，並直接傳遞 `toml::de::Error`。

**判斷依據**：diff 中將原本的 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，並使用 `serde_json::Error::custom` 包裝錯誤字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> Flatpak 的 Display 實作大小寫不一致</summary>

在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

**判斷依據**：diff 中新增的 `Display` 分支回傳 `"Flatpak"`，而其他分支均為小寫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6382 (cache hit 1536) ｜ completion tokens 688 ｜ PR #3</sub>