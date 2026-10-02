<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要變更包括：tauri-bundler 與 tauri-cli 的版本號提升、移除 .changes 目錄下的變更記錄檔、更新 CHANGELOG、以及修改 http_utils.rs 中的 generate_github_alternative_url 函式與移除 HashAlgorithm 的 cfg 屬性。整體風險低，但 http_utils.rs 的修改可能引入行為變更，需確認其正確性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:52` | generate_github_alternative_url 可能忽略替代 URL 而使用原始 URL | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:99` | 移除 HashAlgorithm::Sha256 的 cfg 屬性可能導致非 Windows 平台編譯錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:52</code> generate_github_alternative_url 可能忽略替代 URL 而使用原始 URL</summary>

在 `generate_github_alternative_url` 函式中，原本的 `.map(|alt_url| { ... alt_url ... })` 被改為 `.map(|_alt_url| { ... url.to_owned() ... })`。這表示即使成功產生替代 URL，函式仍回傳原始 URL，可能導致下載失敗或繞過鏡像站。請確認此變更是否為預期行為，若非預期，應保留使用 `alt_url`。

**判斷依據**：diff 中將 `alt_url` 改為 `_alt_url`，並將回傳的 URL 從 `alt_url` 改為 `url.to_owned()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:99</code> 移除 HashAlgorithm::Sha256 的 cfg 屬性可能導致非 Windows 平台編譯錯誤</summary>

原本 `HashAlgorithm::Sha256` 帶有 `#[cfg(target_os = "windows")]`，現在被移除。若 `Sha256` 變體在非 Windows 平台未被使用，可能觸發 dead_code 警告；若在其他平台有使用，則需確認相依 crate 是否支援。請確認此變更不會造成編譯問題。

**判斷依據**：diff 中移除了 `#[cfg(target_os = "windows")]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4701 (cache hit 4608) ｜ completion tokens 638 ｜ PR #7</sub>