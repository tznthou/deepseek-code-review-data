<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要變更包括：tauri-bundler 與 tauri-cli 的版本號遞增、CHANGELOG 更新、Cargo.lock 同步，以及兩個程式碼修正：修正 `generate_github_alternative_url` 中錯誤使用替代 URL 的問題，以及移除 `HashAlgorithm` 中不必要的 `cfg(target_os = "windows")` 條件。整體風險低，但需注意 `generate_github_alternative_url` 的修改可能影響 GitHub 下載的備援機制。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:52` | generate_github_alternative_url 不再使用替代 URL，可能導致下載失敗 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:99` | 移除 HashAlgorithm::Sha256 的 cfg 條件可能影響跨平台編譯 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:52</code> generate_github_alternative_url 不再使用替代 URL，可能導致下載失敗</summary>

在 `generate_github_alternative_url` 中，原本會將 `alt_url`（替代 URL）作為回傳值，但修改後改為回傳原始的 `url`。這使得函式失去其設計目的（提供 GitHub 下載的替代鏡像），當原始 URL 無法存取時，將無法自動切換到替代來源，可能導致下載失敗。

建議：確認此修改是否為預期行為。若需保留替代 URL 功能，應回傳 `alt_url`；若不再需要，應考慮移除整個函式或調整其邏輯。

**判斷依據**：diff 中將 `alt_url` 改為 `url.to_owned()`，且參數改名為 `_alt_url` 表示不再使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:99</code> 移除 HashAlgorithm::Sha256 的 cfg 條件可能影響跨平台編譯</summary>

原本 `HashAlgorithm::Sha256` 帶有 `#[cfg(target_os = "windows")]`，表示該變體僅在 Windows 上可用。移除後，Sha256 將在所有平台上可用，這可能是有意為之（例如其他平台也需要使用 SHA-256），但也可能導致非 Windows 平台出現未預期的編譯或行為變化。

建議：確認所有使用 `HashAlgorithm::Sha256` 的程式碼路徑是否已正確處理跨平台情況。

**判斷依據**：diff 中移除了 `#[cfg(target_os = "windows")]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4701 (cache hit 1408) ｜ completion tokens 709 ｜ PR #7</sub>