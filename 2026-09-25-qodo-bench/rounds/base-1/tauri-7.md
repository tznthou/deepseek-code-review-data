<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要變更包括：tauri-bundler 與 tauri-cli 版本號提升、CHANGELOG 更新、移除 .changes 目錄下的變更記錄檔，以及修正 http_utils.rs 中 generate_github_alternative_url 函式忽略替代 URL 的錯誤。整體風險低，但 http_utils.rs 的修改可能影響 GitHub 下載的備援機制，建議確認其正確性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:52` | generate_github_alternative_url 忽略替代 URL，可能導致下載失敗 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:99` | 移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 條件可能影響跨平台行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:52</code> generate_github_alternative_url 忽略替代 URL，可能導致下載失敗</summary>

在 `generate_github_alternative_url` 函式中，原本應回傳替代 URL（`alt_url`），但修改後改為回傳原始 URL（`url.to_owned()`）。這會使函式失去備援功能：當原始 GitHub URL 無法存取時，原本設計的鏡像站或替代來源將不會被使用，可能導致下載失敗。

**失敗情境**：當使用者位於無法直接存取 GitHub 的環境（例如某些地區或企業網路），且設定了 GitHub 鏡像站時，此函式會忽略鏡像 URL，仍嘗試從原始 GitHub 下載，導致建置工具下載失敗。

**建議**：確認此修改是否為預期行為。若需保留備援機制，應回傳 `alt_url`；若因其他原因需使用原始 URL，請在 PR 描述中說明理由。

**判斷依據**：diff 中將原本的 `alt_url` 改為 `url.to_owned()`，且參數改名為 `_alt_url` 表示刻意忽略。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:99</code> 移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 條件可能影響跨平台行為</summary>

原本 `HashAlgorithm::Sha256` 僅在 Windows 上啟用，現在移除條件編譯後，所有平台皆可使用 Sha256。這可能是為了修正跨平台雜湊驗證問題，但需確認在其他平台（如 Linux、macOS）上使用 Sha256 是否會造成行為變更或與既有邏輯衝突。

**建議**：確認此變更是否為預期，並檢查是否有其他程式碼依賴此條件編譯。

**判斷依據**：diff 中移除了 `#[cfg(target_os = "windows")]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4737 (cache hit 1536) ｜ completion tokens 754 ｜ PR #7</sub>