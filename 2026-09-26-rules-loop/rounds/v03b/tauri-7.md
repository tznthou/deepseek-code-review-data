<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要包含：移除 .changes 目錄下的變更檔案、更新 Cargo.lock、Cargo.toml、CHANGELOG.md 與 metadata-v2.json 的版本號，以及修改 tauri-bundler 的 http_utils.rs。風險在於 http_utils.rs 中 generate_github_alternative_url 函式的行為變更：原本使用替代 URL，現在改回原始 URL，可能導致 GitHub 下載失敗時無法使用鏡像站。此外，移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 條件編譯，使 Sha256 在所有平台可用，需確認此變更是否為預期。整體而言，版本更新部分無重大問題，但 http_utils.rs 的變更需要進一步確認。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:52` | generate_github_alternative_url 不再使用替代 URL | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:99` | 移除 Sha256 的 Windows 條件編譯 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:52</code> generate_github_alternative_url 不再使用替代 URL</summary>

在 generate_github_alternative_url 函式中，原本會將替代 URL (alt_url) 作為回傳值，但現在改為回傳原始 URL (url.to_owned())。這可能導致當 GitHub 下載失敗時，無法使用鏡像站進行下載，進而影響建置流程。請確認此變更是否為預期行為，或是否應保留替代 URL 的邏輯。

**判斷依據**：diff 中顯示原本回傳 alt_url，現在改為 url.to_owned()，且參數名稱改為 _alt_url 表示未使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:99</code> 移除 Sha256 的 Windows 條件編譯</summary>

原本 HashAlgorithm::Sha256 只在 Windows 平台可用，現在移除 cfg(target_os = "windows")，使 Sha256 在所有平台可用。這可能是有意為之，但需確認是否會影響其他平台的雜湊驗證邏輯。

**判斷依據**：diff 中移除了 #[cfg(target_os = "windows")] 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6829 (cache hit 6784) ｜ completion tokens 656 ｜ PR #7</sub>