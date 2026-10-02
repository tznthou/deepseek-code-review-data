<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml 依賴從 0.8 升級至 0.9，並更新相關依賴（toml_edit、serde、winnow 等），同時新增 Flatpak bundle 類型。主要風險在於 toml 0.9 的 API 變更可能導致編譯錯誤或行為差異，且 parse.rs 中的錯誤處理改為使用 ConfigError::FormatJson 可能造成錯誤類型不匹配。此外，新增的 Flatpak 變體可能影響既有 match 陳述式的完整性。建議先確認所有使用 toml 的程式碼已相容，並修正錯誤處理邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤處理不當：將 TOML 解析錯誤包裝為 FormatJson | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 可能導致下游 match 不完整 | 0.60 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | Display 實作中 Flatpak 的大小寫不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤處理不當：將 TOML 解析錯誤包裝為 FormatJson</summary>

在 `do_parse_toml` 中，原本使用 `ConfigError::FormatToml` 來封裝 TOML 解析錯誤，但升級後改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會導致錯誤類型不正確，可能使呼叫端無法正確處理 TOML 格式錯誤，且錯誤訊息可能具有誤導性。建議保留 `FormatToml` 變體，或新增專用的 TOML 錯誤變體。

**判斷依據**：diff 中將原本的 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，並使用 `serde_json::Error::custom` 包裝錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 可能導致下游 match 不完整</summary>

新增 `BundleType::Flatpak` 變體後，所有對 `BundleType` 進行 exhaustive match 的下游程式碼（包括使用者程式碼）都會因缺少分支而無法編譯。雖然這是預期的 API 變更，但需要確認是否已更新所有內部 match，並考慮是否應標記為 `#[non_exhaustive]` 以減少破壞性。

**判斷依據**：diff 中新增了 `Flatpak` 變體，且未標記 `#[non_exhaustive]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> Display 實作中 Flatpak 的大小寫不一致</summary>

在 `Display` 實作中，`Flatpak` 被輸出為 "Flatpak"（首字母大寫），而其他變體如 "nsis"、"app"、"dmg" 均為小寫。這可能導致序列化或顯示時的不一致，建議統一為小寫 "flatpak"。

**判斷依據**：diff 中新增的 Display 分支使用大寫開頭，與其他分支風格不符。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8454 (cache hit 6272) ｜ completion tokens 863 ｜ PR #3</sub>