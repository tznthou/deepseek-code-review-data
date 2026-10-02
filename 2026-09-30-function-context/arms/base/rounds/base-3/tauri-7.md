<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，包含 tauri-bundler 與 tauri-cli 的版本號提升、變更日誌更新，以及兩個程式碼修正：修正 GitHub 鏡像 URL 回退邏輯，以及移除 HashAlgorithm::Sha256 的 Windows 限定。整體風險低，但鏡像 URL 修正可能導致非 GitHub 網址被錯誤改寫，建議確認。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:52` | 鏡像 URL 回退邏輯可能錯誤改寫非 GitHub 網址 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:99` | 移除 Sha256 的 Windows 限定可能影響跨平台行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:52</code> 鏡像 URL 回退邏輯可能錯誤改寫非 GitHub 網址</summary>

在 `generate_github_alternative_url` 中，原本回傳替代 URL（`alt_url`），現在改為回傳原始 URL（`url.to_owned()`）。這可能導致當 `generate_github_mirror_url_from_template` 或 `generate_github_mirror_url_from_base` 成功產生鏡像 URL 時，函式卻回傳原始 URL，使得鏡像功能失效。此外，若原始 URL 不是 GitHub 網址，此函式仍可能被呼叫並回傳原始 URL，但呼叫端可能預期只有 GitHub 網址會被處理。建議確認此函式的呼叫情境，並確保只有 GitHub 網址會進入此邏輯，或修正回傳值為 `alt_url`。

**判斷依據**：diff 中將 `alt_url` 改為 `url.to_owned()`，且參數改名為 `_alt_url` 表示不再使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:99</code> 移除 Sha256 的 Windows 限定可能影響跨平台行為</summary>

原本 `HashAlgorithm::Sha256` 只在 Windows 上可用，現在移除 `#[cfg(target_os = "windows")]`，使其在所有平台可用。這可能是為了支援跨平台雜湊驗證，但需確認是否有其他平台特定邏輯依賴此 cfg。若無其他限制，此變更應屬安全，但建議確認相關使用情境。

**判斷依據**：diff 中移除了 `#[cfg(target_os = "windows")]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4737 (cache hit 4736) ｜ completion tokens 675 ｜ PR #7</sub>