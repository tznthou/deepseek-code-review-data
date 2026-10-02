<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要包含：移除多個 .changes 檔案、更新 Cargo.lock 與各套件版本號、更新 CHANGELOG，以及修改 tauri-bundler 的 http_utils.rs。其中 http_utils.rs 的修改有兩個值得注意的點：generate_github_alternative_url 現在忽略 alt_url 而改用原始 url，可能改變下載來源；另外移除了 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 限制，使其在所有平台可用。整體風險不高，但需確認這些變更符合預期。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:52` | generate_github_alternative_url 忽略 alt_url 可能導致下載來源錯誤 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:99` | 移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 可能影響跨平台行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:52</code> generate_github_alternative_url 忽略 alt_url 可能導致下載來源錯誤</summary>

在 `generate_github_alternative_url` 中，原本使用 `alt_url` 作為下載 URL，但修改後改為使用原始的 `url`。這可能導致當 GitHub 下載失敗時，備援機制失效，因為它仍然嘗試從原始 URL 下載，而不是使用替代的鏡像 URL。

**失敗情境**：當 GitHub 主要 URL 無法存取（例如網路問題或 GitHub 暫時故障），原本的備援機制會嘗試從鏡像下載，但修改後會再次嘗試相同的原始 URL，導致下載失敗。

**建議**：確認此修改是否為預期行為。如果目的是為了避免使用替代 URL，則應移除整個備援機制；否則應保留 `alt_url` 的使用。

**判斷依據**：diff 中將 `alt_url` 改為 `_alt_url`，並將回傳的 URL 從 `alt_url` 改為 `url.to_owned()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:99</code> 移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 可能影響跨平台行為</summary>

原本 `HashAlgorithm::Sha256` 只在 Windows 上可用，現在移除 cfg 限制後，在所有平台都可用。這可能是有意的，但需確認在其他平台上使用 SHA-256 是否會造成問題（例如效能或相容性）。

**建議**：確認此變更是否為預期，並確保在其他平台上的測試涵蓋此路徑。

**判斷依據**：diff 中移除了 `#[cfg(target_os = "windows")]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5792 (cache hit 5760) ｜ completion tokens 741 ｜ PR #7</sub>