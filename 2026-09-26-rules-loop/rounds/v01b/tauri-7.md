<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要變更包括：移除 .changes 目錄下的變更檔案、更新 Cargo.lock 與各 crate 版本號、調整 http_utils.rs 中的 URL 處理邏輯、移除 HashAlgorithm 的 Windows 條件編譯，以及更新 CHANGELOG 與 metadata。整體風險低，但 http_utils.rs 的修改可能引入行為變更，需確認其正確性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:58` | generate_github_alternative_url 可能忽略替代 URL 並使用原始 URL | 0.75 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:100` | 移除 HashAlgorithm::Sha256 的 Windows 條件編譯可能影響跨平台行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:58</code> generate_github_alternative_url 可能忽略替代 URL 並使用原始 URL</summary>

在 `generate_github_alternative_url` 中，原本使用 `alt_url`（替代 URL）作為回傳值，但修改後改為 `url.to_owned()`（原始 URL）。這可能導致函式失去其設計目的（提供替代下載來源），並在原始 URL 失效時無法 fallback。請確認此變更是否為預期行為，並考慮保留替代 URL 的邏輯。

**判斷依據**：diff 中將 `alt_url` 改為 `url.to_owned()`，且參數名稱改為 `_alt_url`，暗示不再使用替代 URL。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:100</code> 移除 HashAlgorithm::Sha256 的 Windows 條件編譯可能影響跨平台行為</summary>

原本 `Sha256` 變體僅在 Windows 上可用，現在移除 `#[cfg(target_os = "windows")]` 後，所有平台皆可使用。這可能是有意為之，但需確認其他平台是否已正確處理 SHA-256 驗證，避免在非 Windows 平台出現未預期的行為。

**判斷依據**：diff 中移除了 `#[cfg(target_os = "windows")]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6819 (cache hit 6784) ｜ completion tokens 540 ｜ PR #7</sub>