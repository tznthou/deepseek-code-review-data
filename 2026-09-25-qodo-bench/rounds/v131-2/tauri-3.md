<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml crate 從 0.8 升級至 0.9，並連帶更新多個相依套件（如 toml_edit、serde、winnow 等），同時新增 Flatpak bundle type。升級本身風險不高，但 config.rs 中 `do_parse_toml` 的錯誤處理被改為回報 `FormatJson`，這會誤導使用者，且可能影響依賴錯誤類型的程式碼。建議修正錯誤類型後即可合併。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | TOML 解析錯誤被錯誤地回報為 JSON 格式錯誤 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> TOML 解析錯誤被錯誤地回報為 JSON 格式錯誤</summary>

在 `do_parse_toml` 中，原本將 `toml::from_str` 的錯誤包裝為 `ConfigError::FormatToml`，但升級後改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會導致 TOML 解析失敗時，使用者看到「JSON 格式錯誤」的訊息，造成混淆。此外，若其他程式碼依賴 `ConfigError::FormatToml` 來處理 TOML 錯誤，此變更會破壞其邏輯。建議保留 `FormatToml` 變體，或新增專屬的 TOML 錯誤變體，並正確傳遞原始錯誤。

**判斷依據**：diff 中顯示原本的 `ConfigError::FormatToml` 被改為 `ConfigError::FormatJson`，且錯誤被轉為 `serde_json::Error`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6346 (cache hit 6272) ｜ completion tokens 467 ｜ PR #3</sub>