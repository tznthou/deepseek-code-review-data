<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml 相關 crate 從 0.8 升級至 0.9，並新增 Flatpak bundle 類型。升級本身風險較低，但 config.rs 中 `Display` 實作將 Flatpak 顯示為 "Flatpak"（大寫 F），與其他 bundle 類型的小寫慣例不一致，可能導致序列化或顯示問題。此外，parse.rs 中錯誤處理從 `FormatToml` 改為 `FormatJson`，可能造成錯誤分類不正確，影響使用者診斷。建議修正這兩個問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:180` | Flatpak 的 Display 實作使用大寫 "Flatpak"，與其他 bundle 類型的小寫慣例不一致 | 0.80 |
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | TOML 解析錯誤被錯誤地包裝為 FormatJson，而非 FormatToml | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:180</code> Flatpak 的 Display 實作使用大寫 "Flatpak"，與其他 bundle 類型的小寫慣例不一致</summary>

在 `Display for BundleType` 的實作中，新增的 `Flatpak` 分支回傳 `"Flatpak"`，但其他所有分支（如 `"nsis"`, `"app"`, `"dmg"`）皆為小寫。這可能導致序列化或顯示時的不一致，例如在錯誤訊息或日誌中出現大小寫混雜。建議改為 `"flatpak"` 以維持一致性。

**判斷依據**：diff 中新增的該行明確顯示回傳字串為 "Flatpak"，而其他分支皆為小寫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> TOML 解析錯誤被錯誤地包裝為 FormatJson，而非 FormatToml</summary>

原本的程式碼將 TOML 解析錯誤包裝為 `ConfigError::FormatToml`，但修改後改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會導致錯誤分類不正確，使用者看到 JSON 格式錯誤的訊息，但實際上是 TOML 解析失敗。建議保留 `FormatToml` 變體，或新增專門的 TOML 錯誤變體。

**判斷依據**：diff 中將原本的 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，且錯誤類型從 `toml::de::Error` 改為 `serde_json::Error`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6382 (cache hit 6272) ｜ completion tokens 677 ｜ PR #3</sub>