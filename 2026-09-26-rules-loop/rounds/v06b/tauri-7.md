<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要變更包括：tauri-bundler 與 tauri-cli 版本號提升、移除 .changes 目錄下的變更檔案、更新 CHANGELOG、以及修改 http_utils.rs 中的 URL 處理邏輯。整體風險低，但 http_utils.rs 的變更可能引入行為差異，需確認其正確性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:58` | generate_github_alternative_url 可能忽略鏡像 URL 並使用原始 URL | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:120` | 移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 可能影響跨平台編譯 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:58</code> generate_github_alternative_url 可能忽略鏡像 URL 並使用原始 URL</summary>

在 `generate_github_alternative_url` 中，原本使用 `alt_url`（鏡像 URL）作為回傳值，但修改後改為 `url.to_owned()`（原始 URL）。這可能導致下載時仍使用原始 GitHub URL，而非預期的鏡像 URL，特別是在 GitHub 無法存取或需要鏡像的環境中。請確認此變更是否為預期行為，若非預期，應保留 `alt_url`。

**判斷依據**：diff 中將 `alt_url` 改為 `url.to_owned()`，且變數 `_alt_url` 被忽略，顯示鏡像 URL 未被使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:120</code> 移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 可能影響跨平台編譯</summary>

原本 `HashAlgorithm::Sha256` 僅在 Windows 上啟用，移除 cfg 後將在所有平台啟用。若其他平台未使用 Sha256，可能導致 dead_code 警告或增加編譯大小。請確認此變更是否必要，或考慮保留 cfg 並在需要時啟用。

**判斷依據**：diff 中移除了 `#[cfg(target_os = "windows")]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6809 (cache hit 6784) ｜ completion tokens 540 ｜ PR #7</sub>