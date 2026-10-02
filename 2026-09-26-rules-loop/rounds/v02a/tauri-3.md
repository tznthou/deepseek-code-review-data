<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 toml crate 從 0.8 升級到 0.9，並更新相關依賴（toml_edit、serde、winnow 等），同時在 BundleType 枚舉中新增 Flatpak 變體。主要風險在於 toml 0.9 的 API 變更可能導致解析行為差異，且 do_parse_toml 中的錯誤處理被改為使用 serde_json::Error，可能造成錯誤類型不一致。此外，新增的 Flatpak 變體在 Display 實作中使用了 'Flatpak' 而非小寫 'flatpak'，可能導致序列化不一致。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤處理不當：將 toml 解析錯誤包裝為 serde_json::Error | 0.95 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:180` | Display 實作中 Flatpak 使用大寫 'Flatpak'，可能導致序列化不一致 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 Flatpak 變體可能影響既有 API 相容性 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤處理不當：將 toml 解析錯誤包裝為 serde_json::Error</summary>

在 do_parse_toml 中，原本使用 ConfigError::FormatToml 來封裝 toml 解析錯誤，但現在改為 ConfigError::FormatJson，並將錯誤轉換為 serde_json::Error。這會導致錯誤類型不匹配，且可能遺失 toml 特有的錯誤資訊（如行號、欄位）。建議保留 ConfigError::FormatToml 變體，並直接傳遞 toml::de::Error。

**判斷依據**：diff 中將原本的 ConfigError::FormatToml 改為 ConfigError::FormatJson，並使用 serde_json::Error::custom 轉換錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:180</code> Display 實作中 Flatpak 使用大寫 'Flatpak'，可能導致序列化不一致</summary>

在 Display for BundleType 中，新增的 Flatpak 變體回傳 "Flatpak"，但其他變體皆回傳小寫字串（如 "nsis"、"app"、"dmg"）。這可能導致序列化時產生不一致的輸出，且與 Deserialize 中預期的小寫 "flatpak" 不符。建議改為 "flatpak"。

**判斷依據**：diff 中新增的 Display 分支使用大寫 'Flatpak'，而其他分支皆為小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 Flatpak 變體可能影響既有 API 相容性</summary>

BundleType 為公開枚舉，新增變體可能導致下游程式碼在 exhaustive match 時編譯失敗。若此 crate 遵循 semver，可能需要標記為 breaking change 或使用 #[non_exhaustive]。

**判斷依據**：diff 中新增了 Flatpak 變體，但未見 #[non_exhaustive] 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8464 (cache hit 1536) ｜ completion tokens 837 ｜ PR #3</sub>