<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要更新 tauri、tauri-bundler、tauri-cli 及 @tauri-apps/cli 的版本號，並同步更新 Cargo.lock、CHANGELOG 與 schema 的 $id。變更內容單純，無邏輯改動。但需注意 metadata-v2.json 中 cli.js 版本從 2.8.1 改為 2.8.2，而 tauri-cli 的 Cargo.toml 版本為 2.8.1，可能造成版本不一致。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-cli/metadata-v2.json:3` | cli.js 版本與 tauri-cli 版本不一致 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-cli/metadata-v2.json:3</code> cli.js 版本與 tauri-cli 版本不一致</summary>

metadata-v2.json 中 cli.js 的版本從 2.8.1 更新為 2.8.2，但 tauri-cli 的 Cargo.toml 版本僅從 2.8.0 更新為 2.8.1。這可能導致發布的 CLI 二進制檔案版本與 npm 套件版本不一致，造成使用者混淆或依賴解析問題。建議確認正確的版本號並統一。

**判斷依據**：diff 顯示 metadata-v2.json 中 cli.js 版本改為 2.8.2，而 tauri-cli/Cargo.toml 版本改為 2.8.1。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5718 (cache hit 1408) ｜ completion tokens 392 ｜ PR #9</sub>