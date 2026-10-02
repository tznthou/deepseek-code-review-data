<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要變更包括：tauri-bundler 與 tauri-cli 的版本號提升、CHANGELOG 更新、Cargo.lock 同步，以及 http_utils.rs 中 generate_github_alternative_url 的邏輯變更。風險集中在 http_utils.rs 的修改：原本會回傳替代鏡像 URL，現在改為回傳原始 URL，可能導致下載失敗或行為不符預期。此外，HashAlgorithm 的 cfg 屬性移除可能影響跨平台編譯。建議先確認 http_utils.rs 的變更意圖與影響。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:58` | generate_github_alternative_url 不再回傳替代 URL | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:100` | 移除 HashAlgorithm::Sha256 的 cfg 屬性可能影響跨平台編譯 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:58</code> generate_github_alternative_url 不再回傳替代 URL</summary>

原本函式會回傳替代的鏡像 URL（alt_url），但修改後改為回傳原始 URL（url.to_owned()）。這可能導致 GitHub 下載失敗時無法使用鏡像，或與函式名稱及呼叫端預期不符。請確認此變更是否為刻意行為，並檢查呼叫端是否仍依賴替代 URL。

**判斷依據**：diff 中將 `alt_url` 改為 `url.to_owned()`，且參數名稱從 `alt_url` 改為 `_alt_url`，暗示不再使用替代 URL。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:100</code> 移除 HashAlgorithm::Sha256 的 cfg 屬性可能影響跨平台編譯</summary>

原本 `Sha256` variant 有 `#[cfg(target_os = "windows")]`，現在移除後在所有平台都會啟用。若其他平台原本未使用 Sha256，可能導致未使用的依賴或編譯警告。請確認此變更是否必要。

**判斷依據**：diff 中刪除了 `#[cfg(target_os = "windows")]` 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4845 (cache hit 1536) ｜ completion tokens 555 ｜ PR #7</sub>