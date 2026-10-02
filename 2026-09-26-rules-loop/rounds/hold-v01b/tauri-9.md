<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要更新 tauri、tauri-bundler、tauri-cli 及 @tauri-apps/cli 的版本號，並同步更新 Cargo.lock、CHANGELOG 與 schema 檔案。整體風險低，但發現一個版本不一致問題：crates/tauri-cli/metadata-v2.json 中的 cli.js 版本更新為 2.8.2，但 tauri-cli 的 Cargo.toml 版本為 2.8.1，可能導致發布流程或使用者安裝時版本錯亂。建議修正後再合併。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/metadata-v2.json:3` | 版本不一致：cli.js 版本與 tauri-cli crate 版本不符 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/metadata-v2.json:3</code> 版本不一致：cli.js 版本與 tauri-cli crate 版本不符</summary>

在 `crates/tauri-cli/metadata-v2.json` 中，`cli.js` 的版本從 `2.8.1` 更新為 `2.8.2`，但 `crates/tauri-cli/Cargo.toml` 中的版本僅從 `2.8.0` 更新為 `2.8.1`。這可能導致發布流程中 npm 套件與 Rust crate 版本不一致，或使用者安裝時取得錯誤的版本資訊。請確認正確的版本號並統一更新。

**判斷依據**：diff 中 `crates/tauri-cli/metadata-v2.json` 的 `cli.js` 版本由 `2.8.1` 改為 `2.8.2`，而 `crates/tauri-cli/Cargo.toml` 的版本由 `2.8.0` 改為 `2.8.1`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7836 (cache hit 7808) ｜ completion tokens 462 ｜ PR #9</sub>