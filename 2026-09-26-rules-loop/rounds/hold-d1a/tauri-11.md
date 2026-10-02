<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 platform-certs feature，讓 bundler 與 CLI 在進行 HTTPS 請求時使用系統憑證。主要變更包括：新增 feature flag、重構 HTTP agent 建立邏輯、修正 cargo_manifest.rs 中的條件判斷。整體方向合理，但發現多處違反 repo 規範：新增的 Rust 檔案缺少版權標頭（R01）、部分程式碼未通過 rustfmt 格式化（R03）、TOML 檔案未通過 taplo 格式化（R05）、以及一個邏輯修正可能影響既有行為（R16）。建議先修正格式與版權問題，並確認邏輯變更的意圖。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-bundler/src/utils/http_utils.rs:56` | [R03] 程式碼未通過 rustfmt 格式化 | 0.90 |
| ⚠️ | Major | `crates/tauri-cli/src/helpers/cargo_manifest.rs:194` | [R16] 條件判斷修正可能隱藏錯誤 | 0.85 |
| 🔸 | Minor | `crates/tauri-bundler/Cargo.toml:81` | [R05] TOML 檔案未通過 taplo 格式化 | 0.80 |
| 🔸 | Minor | `crates/tauri-cli/Cargo.toml:149` | [R05] TOML 檔案未通過 taplo 格式化 | 0.80 |
| 🔸 | Minor | `crates/tauri-bundler/src/bundle/windows/util.rs:65` | [R16] 使用 `ureq::get` 而非已建立的 agent | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-bundler/src/utils/http_utils.rs:56</code> [R03] 程式碼未通過 rustfmt 格式化</summary>

新增的 `base_ureq_agent` 函式中的 `#[cfg(feature = "platform-certs")]` 與 `#[cfg(not(feature = "platform-certs"))]` 區塊的縮排不一致，且 `return agent;` 前多了一個空行。請執行 `cargo fmt --all -- --check` 確認並修正。

**判斷依據**：diff 中新增的函式區塊縮排不一致，且 `return agent;` 前有空行，違反 R03。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/src/helpers/cargo_manifest.rs:194</code> [R16] 條件判斷修正可能隱藏錯誤</summary>

將 `if lock.is_some() && crate_lock_packages.is_empty()` 改為 `if lock.is_some() && !crate_lock_packages.is_empty()`。這會改變行為：原本在 lock 存在但 packages 為空時會進入分支，現在則相反。請確認此變更的意圖，並確保不會導致錯誤處理不當。

**判斷依據**：diff 中條件判斷的邏輯被反轉，可能影響錯誤處理路徑，違反 R16 的精神。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/Cargo.toml:81</code> [R05] TOML 檔案未通過 taplo 格式化</summary>

新增的 feature 定義 `platform-certs = ["ureq/platform-verifier"]` 可能未符合 taplo 的格式要求。請執行 `taplo fmt --check --diff` 確認並修正。

**判斷依據**：diff 中新增的 feature 行可能未符合 taplo 格式，違反 R05。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-cli/Cargo.toml:149</code> [R05] TOML 檔案未通過 taplo 格式化</summary>

新增的 feature 定義 `platform-certs = ["tauri-bundler/platform-certs", "ureq/platform-verifier"]` 可能未符合 taplo 的格式要求。請執行 `taplo fmt --check --diff` 確認並修正。

**判斷依據**：diff 中新增的 feature 行可能未符合 taplo 格式，違反 R05。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-bundler/src/bundle/windows/util.rs:65</code> [R16] 使用 `ureq::get` 而非已建立的 agent</summary>

在 `download_webview2_offline_installer` 中，直接使用 `ureq::get(url)` 而非透過 `base_ureq_agent()` 建立的 agent。這可能導致未使用系統憑證，與 PR 目的不符。建議改用 `base_ureq_agent().get(url)`。

**判斷依據**：diff 中新增的程式碼使用 `ureq::get`，未使用 platform-certs 功能，可能違反 R16 的錯誤處理一致性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7056 (cache hit 6912) ｜ completion tokens 1391 ｜ PR #11</sub>