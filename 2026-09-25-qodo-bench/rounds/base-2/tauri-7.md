<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要內容包含：刪除已完成的 changes 檔案、更新 Cargo.toml 與 package.json 版本號、更新 CHANGELOG，以及修改 tauri-bundler 的 http_utils.rs。其中 http_utils.rs 的變更將原本使用替代鏡像 URL 改為使用原始 URL，並移除了 HashAlgorithm 中 Sha256 的 Windows 條件編譯限制。整體風險中等，需確認 URL 變更的意圖與影響，以及移除條件編譯後在非 Windows 平台的行為。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:52` | generate_github_alternative_url 不再使用替代 URL | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:120` | 移除 Sha256 的 Windows 條件編譯限制 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:52</code> generate_github_alternative_url 不再使用替代 URL</summary>

原本函式會產生替代的 GitHub 鏡像 URL（例如處理 GitHub 下載失敗時），但現在直接忽略 `_alt_url` 並回傳原始 `url`。這可能導致原本依賴鏡像 URL 的錯誤處理或效能優化失效。請確認此變更是否為預期行為，並檢查是否有其他程式碼依賴此函式回傳替代 URL。

**判斷依據**：diff 中將 `alt_url` 改為 `_alt_url`，並將回傳的 URL 從 `alt_url` 改為 `url.to_owned()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:120</code> 移除 Sha256 的 Windows 條件編譯限制</summary>

原本 `HashAlgorithm::Sha256` 僅在 Windows 上可用，現在移除 `#[cfg(target_os = "windows")]` 後，所有平台皆可使用。這可能是有意為之（例如其他平台也需要 SHA256），但需確認非 Windows 平台是否有對應的依賴與測試。

**判斷依據**：diff 中刪除了 `#[cfg(target_os = "windows")]` 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4737 (cache hit 4736) ｜ completion tokens 611 ｜ PR #7</sub>