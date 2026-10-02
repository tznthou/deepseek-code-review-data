<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要包含 tauri-bundler 與 tauri-cli 的版本號提升、變更日誌更新，以及 tauri-bundler 中 http_utils.rs 的兩處程式碼變更。主要風險在於 http_utils.rs 中 `generate_github_alternative_url` 函式的修改：原本會回傳替代 URL，現在改為回傳原始 URL，這可能導致 GitHub 下載失敗時無法使用鏡像站作為備援，進而影響建置流程。此外，移除 `HashAlgorithm::Sha256` 的 `#[cfg(target_os = "windows")]` 屬性，使 SHA-256 在所有平台皆可用，這本身是合理的，但需確認其他平台是否已正確處理 SHA-256 驗證。整體而言，變更範圍小，但需特別注意替代 URL 邏輯的變更是否為預期行為。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:58` | 替代 URL 邏輯變更可能導致 GitHub 下載失敗時無法使用鏡像站 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:120` | 移除 `#[cfg(target_os = "windows")]` 可能導致非 Windows 平台出現未預期的 SHA-256 驗證行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:58</code> 替代 URL 邏輯變更可能導致 GitHub 下載失敗時無法使用鏡像站</summary>

在 `generate_github_alternative_url` 函式中，原本會將 `alt_url`（可能是鏡像站 URL）作為回傳值，但修改後改為回傳原始 `url`。這可能導致當 GitHub 下載失敗時，無法使用鏡像站作為備援，進而影響建置流程。

**失敗情境**：當使用者位於無法直接存取 GitHub 的環境（例如某些地區或企業網路），且 `generate_github_mirror_url_from_template` 或 `generate_github_mirror_url_from_base` 成功產生鏡像 URL 時，此函式仍回傳原始 GitHub URL，導致後續下載仍嘗試連線 GitHub，最終失敗。

**建議**：確認此變更是否為預期行為。若目的是為了避免使用鏡像站，則應移除相關的鏡像產生邏輯；否則應保留原本回傳 `alt_url` 的邏輯。

**判斷依據**：diff 中原本的 `alt_url` 被改為 `url.to_owned()`，且參數名稱從 `alt_url` 改為 `_alt_url`，顯示不再使用替代 URL。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:120</code> 移除 `#[cfg(target_os = "windows")]` 可能導致非 Windows 平台出現未預期的 SHA-256 驗證行為</summary>

原本 `HashAlgorithm::Sha256` 僅在 Windows 平台啟用，現在移除條件編譯屬性，使其在所有平台皆可用。這本身是合理的，但需確認其他平台是否已正確處理 SHA-256 驗證，以及是否有任何平台特定邏輯依賴於此條件編譯。

**建議**：確認所有平台皆能正確處理 SHA-256 驗證，且無其他程式碼依賴於此條件編譯。

**判斷依據**：diff 中移除了 `#[cfg(target_os = "windows")]` 屬性，使 `Sha256` 變體在所有平台皆可用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5792 (cache hit 4736) ｜ completion tokens 830 ｜ PR #7</sub>