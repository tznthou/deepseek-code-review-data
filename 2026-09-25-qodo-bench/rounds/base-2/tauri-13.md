<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的多個 crate 版本更新（2.9.0 → 2.9.1 等），主要包含兩項變更：1) 修正 docs.rs 建置失敗的問題；2) 將 tauri-macos-sign 的錯誤型別從 anyhow 改為自訂 Error enum（可能為破壞性變更）。此外，在 notarize_inner 函式中調整了 ditto 命令的參數順序，並修正了狀態判斷的邏輯。整體風險中等，需特別注意 macOS 簽署流程的變更是否正確。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 中 submit_output.status 的判斷邏輯可能反轉 | 0.80 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | ditto 命令參數順序調整可能影響行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 中 submit_output.status 的判斷邏輯可能反轉</summary>

在 `notarize_inner` 函式中，原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 被改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。這會改變當 `status` 為 `None` 時的行為：原本在 `wait` 為 false 時會進入 if 區塊，現在則變成 `wait` 為 true 時才會進入。這可能導致在非等待模式下，即使沒有狀態也不會執行後續的 notarization 邏輯，或在等待模式下錯誤地執行。請確認此變更是否符合預期，並補充對應的測試。

**判斷依據**：diff 中此行由 `if submit_output.status.map_or(!wait, |s| s == "Accepted") {` 改為 `if submit_output.status.map_or(wait, |s| s == "Accepted") {`，邏輯明顯反轉。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> ditto 命令參數順序調整可能影響行為</summary>

在 `notarize_inner` 中，`ditto` 命令的參數順序由原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。雖然 `ditto` 的語法通常允許來源和目標互換，但若路徑包含特殊字元或符號連結，可能導致非預期的行為。建議確認此變更的必要性，並在 macOS 上進行測試。

**判斷依據**：diff 中顯示參數順序由 `app_bundle_path` 在前改為 `zip_path` 在前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10605 (cache hit 10496) ｜ completion tokens 762 ｜ PR #13</sub>