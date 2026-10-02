<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 toml 依賴從 0.8 升級至 0.9，並更新相關 crate（toml_edit、serde、winnow 等）。同時在 BundleType 枚舉中新增 Flatpak 變體。主要風險在於 toml 0.9 的 API 變更可能導致解析行為不同，且 do_parse_toml 中的錯誤處理被改為使用 ConfigError::FormatJson，可能造成錯誤類型混淆。建議確認 toml 0.9 的解析行為與錯誤處理是否符合預期。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-utils/src/config/parse.rs:387` | 錯誤處理變更可能導致錯誤類型混淆 | 0.80 |
| 🔸 | Minor | `crates/tauri-utils/src/config.rs:180` | Display 實作中 Flatpak 的大小寫不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-utils/src/config/parse.rs:387</code> 錯誤處理變更可能導致錯誤類型混淆</summary>

在 do_parse_toml 中，原本使用 ConfigError::FormatToml 來封裝 toml 解析錯誤，但現在改為 ConfigError::FormatJson，並將 toml 錯誤轉為 serde_json::Error。這可能導致錯誤訊息不準確，且呼叫端若依賴錯誤類型來區分格式，將無法正確處理。建議保留 ConfigError::FormatToml 或新增專用錯誤變體。

**判斷依據**：diff 中顯示原本的 ConfigError::FormatToml 被替換為 ConfigError::FormatJson，且錯誤被轉為 serde_json::Error。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-utils/src/config.rs:180</code> Display 實作中 Flatpak 的大小寫不一致</summary>

在 Display for BundleType 中，Flatpak 被輸出為 "Flatpak"（首字母大寫），而其他變體如 "nsis"、"app"、"dmg" 皆為小寫。這可能導致序列化或顯示時的不一致。建議改為 "flatpak" 以維持一致性。

**判斷依據**：diff 中新增的 Display 分支使用 "Flatpak"，而其他分支皆為小寫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6382 (cache hit 6272) ｜ completion tokens 603 ｜ PR #3</sub>