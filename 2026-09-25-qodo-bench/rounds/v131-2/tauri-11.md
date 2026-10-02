<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 `platform-certs` feature，讓 bundler 與 CLI 在進行 HTTPS 請求時使用系統憑證。整體方向合理，但存在幾個需要修正的問題：`generate_github_mirror_url_from_base` 的變更可能破壞 GitHub mirror 功能；`crate_version` 的條件判斷被反轉，可能導致版本解析錯誤；`download_webview2_offline_installer` 未使用統一的 agent，可能無法套用系統憑證。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-bundler/src/utils/http_utils.rs:37` | GitHub mirror URL 設定被移除，可能導致 mirror 功能失效 | 0.95 |
| 🛑 | Blocker | `crates/tauri-cli/src/helpers/cargo_manifest.rs:194` | 條件判斷反轉，可能導致版本解析錯誤 | 0.90 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/windows/util.rs:65` | 下載 WebView2 安裝程式未使用統一的 agent，可能無法套用系統憑證 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:37</code> GitHub mirror URL 設定被移除，可能導致 mirror 功能失效</summary>

在 `generate_github_mirror_url_from_base` 中，原本會將 mirror 的 path 設定為原始 GitHub URL，但此變更移除了 `cdn.set_path(github_url)`，導致 mirror URL 只回傳 mirror 的 base URL，而沒有包含實際的 GitHub 路徑。這會讓所有使用 mirror 的下載請求都指向 mirror 的根路徑，而非正確的檔案位置。

**失敗情境**：當使用者設定 `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` 環境變數時，例如 `https://mirror.example.com`，原本預期會將 `https://github.com/...` 轉換為 `https://mirror.example.com/...`，但現在只會回傳 `https://mirror.example.com`，導致下載失敗。

**建議修法**：恢復 `cdn.set_path(github_url)` 的呼叫，或改用其他方式正確組合 URL。

**判斷依據**：diff 中移除了 `cdn.set_path(github_url);` 這一行，且沒有其他替代邏輯。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-cli/src/helpers/cargo_manifest.rs:194</code> 條件判斷反轉，可能導致版本解析錯誤</summary>

原本的條件是 `if lock.is_some() && crate_lock_packages.is_empty()`，但被改為 `if lock.is_some() && !crate_lock_packages.is_empty()`。這會使得當 lock 檔案存在且 crate 在 lock 中有記錄時，反而進入原本設計給「lock 檔案存在但 crate 不在 lock 中」的分支，可能導致錯誤的版本解析或邏輯錯誤。

**失敗情境**：當使用 Cargo.lock 且 crate 有被鎖定時，原本應該直接使用 lock 中的版本，但現在會進入另一個分支，可能嘗試從網路取得最新版本，或產生不一致的結果。

**建議修法**：將條件改回 `crate_lock_packages.is_empty()`。

**判斷依據**：diff 中將 `crate_lock_packages.is_empty()` 改為 `!crate_lock_packages.is_empty()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/windows/util.rs:65</code> 下載 WebView2 安裝程式未使用統一的 agent，可能無法套用系統憑證</summary>

在 `download_webview2_offline_installer` 中，直接使用 `ureq::get(url)` 建立請求，而不是使用 `base_ureq_agent()`。這會使得此下載不會套用 `platform-certs` feature 所設定的系統憑證，與 PR 的目標不一致。

**失敗情境**：在需要系統憑證的環境（例如企業內部 proxy 或自訂 CA）中，此下載可能因為 TLS 驗證失敗而無法完成。

**建議修法**：改用 `base_ureq_agent().get(url)` 來發送請求。

**判斷依據**：diff 中新增了 `base_ureq_agent` 函式，但此處仍使用 `ureq::get`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4901 (cache hit 4864) ｜ completion tokens 1092 ｜ PR #11</sub>