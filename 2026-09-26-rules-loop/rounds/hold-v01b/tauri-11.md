<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 platform-certs feature，使 bundler 與 CLI 在進行 HTTPS 請求時使用系統憑證。主要變更包括：在 tauri-bundler 與 tauri-cli 的 Cargo.toml 中新增 platform-certs feature 並設為預設、重構 http_utils 以提供 base_ureq_agent、在 cargo_manifest 中改用 platform verifier、以及修正 crate_version 中的邏輯錯誤。整體風險中等：新增的 feature 預設啟用可能影響憑證驗證行為，且 cargo_manifest 中的 agent 未設定 proxy，可能導致企業環境下無法連線。此外，crate_version 的邏輯修正（lock.is_some() && !crate_lock_packages.is_empty()）是正確的，但需確認其影響。建議優先處理 proxy 設定與 feature 預設值的影響評估。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/src/helpers/cargo_manifest.rs:122` | platform-certs 啟用時未設定 proxy，可能導致企業環境下無法連線 | 0.80 |
| ⚠️ | Major | `crates/tauri-bundler/Cargo.toml:77` | platform-certs 設為預設 feature 可能改變憑證驗證行為 | 0.70 |
| 🔸 | Minor | `crates/tauri-bundler/src/utils/http_utils.rs:56` | base_ureq_agent 函式缺少文件註解 | 0.60 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/windows/util.rs:65` | download_webview2_offline_installer 改用 ureq::get 可能失去 proxy 支援 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/cargo_manifest.rs:122</code> platform-certs 啟用時未設定 proxy，可能導致企業環境下無法連線</summary>

在 `crate_latest_version` 中，當 `platform-certs` feature 啟用時，建立的 `ureq::Agent` 未呼叫 `.proxy(ureq::Proxy::try_from_env())`，而原本的 `ureq::get` 會自動使用環境變數中的 proxy。這可能導致在需要 proxy 的環境（如企業網路）中，crates.io 的請求失敗。建議在 agent builder 中加入 proxy 設定，與 `base_ureq_agent` 保持一致。

**判斷依據**：diff 中新增的 agent 建立程式碼未包含 proxy 設定，而原本的 `ureq::get` 會自動處理 proxy。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/Cargo.toml:77</code> platform-certs 設為預設 feature 可能改變憑證驗證行為</summary>

將 `platform-certs` 加入 default features 會使所有使用者預設使用系統憑證驗證。這可能導致在某些系統上（尤其是 Linux）因系統憑證設定不完整而無法建立 TLS 連線，而原本使用 rustls 的 webpki-roots 則可正常運作。建議評估是否應預設啟用，或提供明確的選擇機制。

**判斷依據**：diff 中將 default features 從 `["rustls"]` 改為 `["rustls", "platform-certs"]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:56</code> base_ureq_agent 函式缺少文件註解</summary>

新增的 `pub(crate) fn base_ureq_agent()` 是 crate 內部公開函式，但未提供文件註解。雖然不是 public API，但為了可維護性，建議加上簡短說明其用途與行為。

**判斷依據**：diff 中新增的函式沒有 doc comment。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/windows/util.rs:65</code> download_webview2_offline_installer 改用 ureq::get 可能失去 proxy 支援</summary>

原本使用 `download(url)` 函式（可能包含 proxy 設定），現在改為直接呼叫 `ureq::get(url)`，這可能導致在需要 proxy 的環境下無法下載。建議使用 `base_ureq_agent()` 來建立 agent 並發送請求，以保持 proxy 支援。

**判斷依據**：diff 中將 `download(url)` 替換為 `ureq::get(url)`，未使用 agent。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7019 (cache hit 6912) ｜ completion tokens 1156 ｜ PR #11</sub>