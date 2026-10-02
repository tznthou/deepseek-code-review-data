<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml 依賴從 0.8 升級至 0.9，並更新相關依賴（toml_edit、serde、winnow 等），同時在 BundleType 枚舉中新增 Flatpak 變體。升級可能引入 API 變更，需確認程式碼相容性；新增變體可能影響序列化與匹配邏輯。另外，do_parse_toml 的錯誤處理被改為使用 ConfigError::FormatJson，可能造成錯誤類型混淆。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤處理不當：將 TOML 解析錯誤包裝為 FormatJson | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 可能影響序列化與匹配邏輯 | 0.60 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:209` | 反序列化僅接受小寫 "flatpak"，與 Display 輸出不對稱 | 0.50 |
| 🔸 | Minor | `crates/tauri-cli/Cargo.toml:59` | toml_edit 升級至 0.23 可能引入 API 變更 | 0.40 |
| 🔸 | Minor | `crates/tauri-build/Cargo.toml:46` | toml 升級至 0.9 可能引入 API 變更 | 0.40 |
| 🔸 | Minor | `crates/tauri-plugin/Cargo.toml:38` | toml 升級至 0.9 可能引入 API 變更 | 0.40 |
| 🔸 | Minor | `crates/tauri-utils/Cargo.toml:37` | toml 升級至 0.9 可能引入 API 變更 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤處理不當：將 TOML 解析錯誤包裝為 FormatJson</summary>

在 `do_parse_toml` 中，原本使用 `ConfigError::FormatToml` 來包裝 TOML 解析錯誤，但現在改為使用 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會導致錯誤類型與實際格式不符，可能誤導使用者或呼叫者，且喪失原始錯誤的型別資訊。建議保留 `FormatToml` 變體，或新增專用變體來處理 TOML 錯誤。

**判斷依據**：diff 中顯示原本的 `ConfigError::FormatToml` 被替換為 `ConfigError::FormatJson`，且錯誤被轉換為 `serde_json::Error`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 可能影響序列化與匹配邏輯</summary>

新增 `BundleType::Flatpak` 變體，但未檢查所有對 `BundleType` 的匹配是否已涵蓋新變體。若存在非窮盡匹配，可能導致編譯錯誤或邏輯遺漏。此外，`Display` 實作中回傳的字串為 "Flatpak"（大寫開頭），與其他變體的小寫形式不一致，可能造成序列化或使用者介面顯示問題。

**判斷依據**：diff 中新增了 `Flatpak` 變體，並在 `Display` 中回傳 "Flatpak"，而其他變體如 "nsis"、"app"、"dmg" 皆為小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:209</code> 反序列化僅接受小寫 "flatpak"，與 Display 輸出不對稱</summary>

在 `Deserialize` 實作中，僅接受小寫 "flatpak"，但 `Display` 輸出為 "Flatpak"。這可能導致序列化後再反序列化失敗，或使用者輸入大寫形式時無法解析。建議統一大小寫，或同時接受大小寫。

**判斷依據**：diff 中新增了 `"flatpak" => Ok(Self::Flatpak)`，而 `Display` 輸出為 "Flatpak"。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/Cargo.toml:59</code> toml_edit 升級至 0.23 可能引入 API 變更</summary>

`toml_edit` 從 0.22 升級至 0.23，可能包含破壞性 API 變更。需確認程式碼中使用的 API 是否相容，並檢查是否有編譯錯誤。

**判斷依據**：diff 中將 `toml_edit` 版本從 0.22 改為 0.23。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-build/Cargo.toml:46</code> toml 升級至 0.9 可能引入 API 變更</summary>

`toml` 從 0.8 升級至 0.9，可能包含破壞性 API 變更。需確認程式碼中使用的 API 是否相容，並檢查是否有編譯錯誤。

**判斷依據**：diff 中將 `toml` 版本從 0.8 改為 0.9。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-plugin/Cargo.toml:38</code> toml 升級至 0.9 可能引入 API 變更</summary>

`toml` 從 0.8 升級至 0.9，可能包含破壞性 API 變更。需確認程式碼中使用的 API 是否相容，並檢查是否有編譯錯誤。

**判斷依據**：diff 中將 `toml` 版本從 0.8 改為 0.9。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/Cargo.toml:37</code> toml 升級至 0.9 可能引入 API 變更</summary>

`toml` 從 0.8 升級至 0.9，可能包含破壞性 API 變更。需確認程式碼中使用的 API 是否相容，並檢查是否有編譯錯誤。

**判斷依據**：diff 中將 `toml` 版本從 0.8 改為 0.9。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8392 (cache hit 6400) ｜ completion tokens 1603 ｜ PR #3</sub>