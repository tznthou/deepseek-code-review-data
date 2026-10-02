<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml crate 從 0.8 升級至 0.9，並更新多個相依套件版本。同時在 BundleType 列舉中新增 Flatpak 變體，並修改了 TOML 解析的錯誤處理。主要風險在於 toml 0.9 的 API 變更可能導致編譯錯誤或行為差異，且錯誤處理的變更可能不正確。此外，新增的 Flatpak 變體可能影響序列化與反序列化，需要驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤處理不當：將 TOML 解析錯誤包裝為 JSON 錯誤 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 可能影響序列化與反序列化 | 0.60 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 可能違反 R07（公共 API 缺少文件） | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤處理不當：將 TOML 解析錯誤包裝為 JSON 錯誤</summary>

在 `do_parse_toml` 函數中，原本將 `toml::from_str` 的錯誤包裝為 `ConfigError::FormatToml`，但修改後改為 `ConfigError::FormatJson`，並使用 `serde_json::Error::custom` 包裝錯誤訊息。這可能導致錯誤類型不正確，影響呼叫端的錯誤處理邏輯。建議確認 `ConfigError` 是否有對應的 TOML 錯誤變體，並使用正確的變體。

**判斷依據**：diff 中顯示原本使用 `ConfigError::FormatToml`，修改後改為 `ConfigError::FormatJson`，且錯誤類型從 `toml::de::Error` 改為 `serde_json::Error`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 可能影響序列化與反序列化</summary>

新增 `BundleType::Flatpak` 變體，並在 `Display` 和 `Deserialize` 中處理。但 `Display` 的實作回傳 "Flatpak"（大寫 F），而 `Deserialize` 接受 "flatpak"（小寫）。這可能導致序列化後的字串與反序列化預期不一致。建議確認序列化（如 `Serialize`）的實作是否也使用相同的大小寫，並考慮統一。

**判斷依據**：diff 中新增 `Flatpak` 變體，`Display` 回傳 "Flatpak"，`Deserialize` 接受 "flatpak"。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 可能違反 R07（公共 API 缺少文件）</summary>

新增的 `BundleType::Flatpak` 變體有文件註解，但 `Display` 和 `Deserialize` 的實作沒有新增對應的文件。雖然不是必要，但建議補充說明以符合專案規範。

**判斷依據**：diff 中新增變體，但未見對應的 `Display` 或 `Deserialize` 文件更新。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8464 (cache hit 8448) ｜ completion tokens 873 ｜ PR #3</sub>