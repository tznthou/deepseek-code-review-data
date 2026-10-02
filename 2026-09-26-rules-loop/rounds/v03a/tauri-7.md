<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要包含 tauri-bundler 與 tauri-cli 的版本號遞增、CHANGELOG 更新，以及 tauri-bundler 中 http_utils.rs 的兩處程式碼變更。整體風險低，但 http_utils.rs 的變更可能引入功能性問題：generate_github_alternative_url 現在忽略替代 URL 而使用原始 URL，可能破壞 GitHub 下載的鏡像/替代機制；移除 Sha256 的 cfg 限制可能導致非 Windows 平台編譯錯誤。建議確認這些變更的意圖與影響。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:58` | generate_github_alternative_url 忽略替代 URL，可能破壞下載功能 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:120` | 移除 Sha256 的 cfg 限制可能導致非 Windows 平台編譯錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:58</code> generate_github_alternative_url 忽略替代 URL，可能破壞下載功能</summary>

在 `generate_github_alternative_url` 中，原本使用 `alt_url` 作為下載 URL，但變更後改為使用原始的 `url`。這可能導致當原始 URL 無法訪問時，原本設計的替代 URL（例如 GitHub 鏡像）不再被使用，造成下載失敗。

建議確認此變更的意圖：若是有意為之，請在程式碼中加上註解說明原因；否則應保留使用 `alt_url` 的邏輯。

**判斷依據**：diff 中 `-        alt_url,` 改為 `+        url.to_owned(),`，且參數名稱從 `alt_url` 改為 `_alt_url`，顯示替代 URL 被刻意忽略。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:120</code> 移除 Sha256 的 cfg 限制可能導致非 Windows 平台編譯錯誤</summary>

原本 `HashAlgorithm::Sha256` 帶有 `#[cfg(target_os = "windows")]`，現在被移除。若 `Sha256` 變體在其他平台未被使用，可能觸發 dead_code 警告（若啟用 `-D warnings` 則會編譯失敗）。此外，若 `Sha256` 的實作依賴 Windows 特定功能，移除 cfg 可能導致其他平台編譯錯誤。

建議確認 `Sha256` 在所有平台上的可用性，或保留 cfg 限制。

**判斷依據**：diff 中刪除了 `#[cfg(target_os = "windows")]` 行，且 `Sha256` 變體現在無條件編譯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6829 (cache hit 4608) ｜ completion tokens 667 ｜ PR #7</sub>