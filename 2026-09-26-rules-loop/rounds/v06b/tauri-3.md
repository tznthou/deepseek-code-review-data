<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 toml crate 從 0.8 升級至 0.9，並更新相關依賴（toml_edit、serde、winnow 等），同時新增 Flatpak bundle type。升級可能引入 API 變更，需確認程式碼相容性。最關鍵的問題是 parse.rs 中錯誤處理的變更：將 TOML 解析錯誤包裝成 FormatJson，可能導致錯誤類型不正確且遺失原始錯誤資訊。此外，新增的 BundleType::Flatpak 的 Display 實作使用大寫 'Flatpak'，與其他 variant 的小寫慣例不一致，可能造成序列化或比對問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-utils/src/config/parse.rs:387` | TOML 解析錯誤被錯誤地包裝為 FormatJson | 0.95 |
| ⚠️ | Major | `crates/tauri-utils/src/config.rs:180` | BundleType::Flatpak 的 Display 實作使用大寫，與其他 variant 不一致 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增的 BundleType::Flatpak 可能違反 R07（缺少文件） | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> TOML 解析錯誤被錯誤地包裝為 FormatJson</summary>

在 `do_parse_toml` 中，原本將 `toml::from_str` 的錯誤包裝為 `ConfigError::FormatToml`，但現在改為 `ConfigError::FormatJson`，並將錯誤轉為字串後放入 `serde_json::Error`。這會導致錯誤類型不正確，且遺失原始錯誤的結構化資訊（如行號、欄位）。呼叫端若依賴 `FormatToml` 來處理 TOML 錯誤，將無法正確運作。建議保留 `FormatToml` variant，並直接傳遞 `toml::de::Error`。

**判斷依據**：diff 中將 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，並使用 `serde_json::Error::custom` 包裝錯誤字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config.rs:180</code> BundleType::Flatpak 的 Display 實作使用大寫，與其他 variant 不一致</summary>

新增的 `BundleType::Flatpak` 在 `Display` 實作中回傳 `"Flatpak"`，而其他 variant 皆回傳小寫（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或比對時出現不一致，例如在 CLI 參數或設定檔中預期小寫。建議改為 `"flatpak"` 以維持一致性。

**判斷依據**：diff 中新增的 `Display` 分支回傳 `"Flatpak"`，而其他分支皆為小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增的 BundleType::Flatpak 可能違反 R07（缺少文件）</summary>

新增的 enum variant `Flatpak` 沒有文件註解，而其他 variant 都有 `///` 說明。根據 R07，公開 API 應包含文件。建議補上說明，例如 `/// The Flatpak bundle (.flatpak).`

**判斷依據**：diff 中新增的 variant 上方有註解，但可能不符合既有格式？

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8454 (cache hit 8448) ｜ completion tokens 901 ｜ PR #3</sub>