<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 tauri-bundler 與 tauri-cli 新增 `platform-certs` feature，使其在進行 HTTPS 請求時使用系統憑證。主要變更包括：新增 feature 定義、重構 agent 建立邏輯、修改 WebView2 下載流程，以及修正 `crate_version` 中的條件判斷。整體方向合理，但存在一個嚴重的邏輯錯誤（條件反轉）可能導致版本解析錯誤，以及一些錯誤處理與資源管理的疑慮。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `crates/tauri-cli/src/helpers/cargo_manifest.rs:194` | 條件判斷反轉，導致 lock_version 永遠無法被設定 | 0.95 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/windows/util.rs:65` | 下載 WebView2 離線安裝程式時未使用代理設定 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/src/bundle/windows/util.rs:65` | 下載 WebView2 離線安裝程式時未檢查 HTTP 狀態碼 | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:37` | `generate_github_mirror_url_from_base` 中移除了 `set_path` 呼叫，可能導致鏡像 URL 不正確 | 0.60 |
| 🔸 | Minor | `crates/tauri-cli/src/helpers/cargo_manifest.rs:121` | `crate_latest_version` 中錯誤處理不一致 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>crates/tauri-cli/src/helpers/cargo_manifest.rs:194</code> 條件判斷反轉，導致 lock_version 永遠無法被設定</summary>

原本的條件是 `lock.is_some() && crate_lock_packages.is_empty()`，但邏輯上應該是在 lock 存在且 crate_lock_packages 不為空時才設定 lock_version。此變更將條件改為 `!crate_lock_packages.is_empty()`，但這會使得當 crate_lock_packages 為空時（例如找不到對應套件）反而進入設定 lock_version 的區塊，而此時 `crate_lock_packages` 為空，`lock_version` 會是空字串，最終不會被設定。反之，當 crate_lock_packages 不為空時，條件為 false，不會設定 lock_version。這將導致 lock_version 永遠無法被正確設定，可能影響依賴版本解析。

建議改回 `lock.is_some() && crate_lock_packages.is_empty()`，或根據實際需求調整條件。

**判斷依據**：diff 中將原本的 `if lock.is_some() && crate_lock_packages.is_empty() {` 改為 `if lock.is_some() && !crate_lock_packages.is_empty() {`，但後續程式碼使用 `crate_lock_packages` 來產生 lock_version，若為空則 lock_version 為空字串，不會被設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/windows/util.rs:65</code> 下載 WebView2 離線安裝程式時未使用代理設定</summary>

在 `download_webview2_offline_installer` 中，原本使用 `download(url)` 函式（可能內部有處理代理），但改為直接使用 `ureq::get(url)`，這會忽略代理設定。若使用者在需要代理的環境下執行，下載可能失敗。建議改用 `base_ureq_agent()` 或確保代理設定被套用。

**判斷依據**：diff 中將 `std::fs::write(&file_path, download(url)?)?;` 改為直接呼叫 `ureq::get(url)`，未使用先前建立的 agent，可能遺失代理設定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/bundle/windows/util.rs:65</code> 下載 WebView2 離線安裝程式時未檢查 HTTP 狀態碼</summary>

直接使用 `ureq::get(url).call()` 後未檢查回應狀態碼，若伺服器回傳 404 或其他錯誤，仍會將錯誤頁面內容寫入檔案。建議檢查 `response.status()` 或使用 `response.into_body().read_to_end()` 前先確認狀態碼為 2xx。

**判斷依據**：diff 中新增的程式碼未對 response 狀態碼進行檢查，直接讀取 body。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:37</code> `generate_github_mirror_url_from_base` 中移除了 `set_path` 呼叫，可能導致鏡像 URL 不正確</summary>

原本的程式碼會將 `cdn` 的 path 設定為 `github_url`，但修改後僅回傳 `cdn.to_string()`，這可能導致鏡像 URL 未包含正確的路徑。若 `cdn` 原本有 path，則可能無法正確替換。建議確認此變更是否為預期行為，或改為使用 `Url::parse` 並正確設定 path。

**判斷依據**：diff 中移除了 `cdn.set_path(github_url);`，僅回傳 `cdn.to_string()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/src/helpers/cargo_manifest.rs:121</code> `crate_latest_version` 中錯誤處理不一致</summary>

在 `platform-certs` feature 啟用時，使用 `agent.get(&url).call().ok()?` 來處理錯誤，但未檢查 HTTP 狀態碼。若伺服器回傳非 2xx，仍會嘗試解析 JSON，可能導致 panic。建議檢查狀態碼或使用 `response.into_body().read_to_string()` 前先確認狀態。

**判斷依據**：diff 中新增的程式碼未檢查 response 狀態碼，直接使用 `serde_json::from_reader`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5858 (cache hit 1536) ｜ completion tokens 1510 ｜ PR #11</sub>