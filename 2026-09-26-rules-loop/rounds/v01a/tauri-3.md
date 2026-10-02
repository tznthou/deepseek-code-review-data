<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml 依賴從 0.8 升級至 0.9，並更新相關 crate（toml_edit、serde、winnow 等），同時在 BundleType 枚舉中新增 Flatpak 變體。升級可能引入 API 變更，需確認程式碼相容性；新增 Flatpak 變體可能影響序列化與反序列化，且 Display 實作使用大寫開頭，與其他變體不一致。此外，do_parse_toml 的錯誤處理從 FormatToml 改為 FormatJson，可能導致錯誤類型不匹配。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | do_parse_toml 錯誤處理改為 FormatJson，可能導致錯誤類型不匹配 | 0.75 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | BundleType::Flatpak 的 Display 實作使用大寫開頭，與其他變體不一致 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 可能影響序列化與反序列化相容性 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> do_parse_toml 錯誤處理改為 FormatJson，可能導致錯誤類型不匹配</summary>

原本使用 `ConfigError::FormatToml` 來封裝 toml 解析錯誤，現在改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這可能導致呼叫端預期 `FormatToml` 錯誤變體時無法正確處理，且錯誤訊息可能不準確。建議確認 `ConfigError` 的定義，若需要保留 TOML 錯誤類型，應新增對應變體或使用更通用的錯誤封裝。

**判斷依據**：diff 中將 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，並使用 `serde_json::Error::custom` 包裝 toml 錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> BundleType::Flatpak 的 Display 實作使用大寫開頭，與其他變體不一致</summary>

在 `Display` 實作中，`Self::Flatpak => "Flatpak"` 使用大寫開頭，而其他變體如 `"nsis"`、`"app"`、`"dmg"` 均為小寫。這可能導致序列化輸出不統一，若下游依賴小寫字串進行比對或顯示，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

**判斷依據**：diff 中新增行 `Self::Flatpak => "Flatpak",`，與其他變體的小寫字串形成對比。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 可能影響序列化與反序列化相容性</summary>

新增 `Flatpak` 變體後，若 `BundleType` 被序列化為字串（如 JSON），舊版程式可能無法識別 `"flatpak"`。此外，`Deserialize` 實作已加入 `"flatpak"` 的對應，但若外部系統使用大寫 `"Flatpak"` 則無法解析。建議確認序列化格式的相容性需求，並考慮是否需要版本遷移。

**判斷依據**：diff 中新增 `Flatpak` 變體，並在 `Deserialize` 中新增 `"flatpak"` 對應，但 `Display` 輸出為 `"Flatpak"`，可能造成不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8464 (cache hit 6272) ｜ completion tokens 938 ｜ PR #3</sub>