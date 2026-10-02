<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml 依賴從 0.8 升級至 0.9，並更新相關 crate（toml_edit、winnow 等），同時新增 BundleType::Flatpak 變體。升級可能導致 API 行為變更，需確認所有使用 toml 的程式碼已相容。此外，do_parse_toml 的錯誤處理改為使用 ConfigError::FormatJson，可能造成錯誤訊息誤導，且未新增對應測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤處理不當：將 TOML 解析錯誤包裝為 FormatJson | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:147` | 新增 BundleType::Flatpak 但未更新所有相關邏輯 | 0.70 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | Display 實作中 Flatpak 的大小寫不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤處理不當：將 TOML 解析錯誤包裝為 FormatJson</summary>

在 `do_parse_toml` 中，原本使用 `ConfigError::FormatToml` 來封裝 TOML 解析錯誤，但現在改為 `ConfigError::FormatJson`，並將錯誤轉為字串後包裝成 `serde_json::Error`。這會導致錯誤類型不正確，可能誤導使用者或呼叫者，且喪失結構化錯誤資訊。建議保留 `FormatToml` 變體，或新增專門的 TOML 錯誤變體，並直接傳遞原始錯誤。

**判斷依據**：diff 中將 `ConfigError::FormatToml` 改為 `ConfigError::FormatJson`，並使用 `serde_json::Error::custom` 包裝錯誤字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:147</code> 新增 BundleType::Flatpak 但未更新所有相關邏輯</summary>

新增 `BundleType::Flatpak` 變體，但可能需要在其他 match 或邏輯中處理此新變體，例如在 `BundleType::all()` 中已加入，但需確認是否有其他 exhaustive match 或序列化邏輯需要更新。

**判斷依據**：diff 中新增了 `Flatpak` 變體，但未顯示其他相關程式碼的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> Display 實作中 Flatpak 的大小寫不一致</summary>

在 `Display` 實作中，`Flatpak` 的輸出為 `"Flatpak"`（首字母大寫），而其他變體如 `"nsis"`、`"app"`、`"dmg"` 均為小寫。這可能導致序列化或顯示時的不一致。建議改為 `"flatpak"` 以維持一致性。

**判斷依據**：diff 中新增的 Display 分支使用大寫開頭。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7437 (cache hit 6272) ｜ completion tokens 814 ｜ PR #3</sub>