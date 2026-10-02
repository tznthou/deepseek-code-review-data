<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的多個 crate 進行版本更新（patch/minor），主要包含：移除已完成的 change files、更新 Cargo.lock 與各 Cargo.toml 版本、更新 CHANGELOG、以及將 tauri-macos-sign 的錯誤型別從 thiserror 改為手動實作 Display/Error。整體風險低，但 tauri-macos-sign 的錯誤處理變更可能影響下游依賴，且需確認是否符合專案規範（R08、R09）。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R08] 錯誤型別未使用 thiserror，可能違反專案規範 | 0.80 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開錯誤枚舉未標記 #[non_exhaustive] | 0.70 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 中條件判斷邏輯可能反轉 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R08] 錯誤型別未使用 thiserror，可能違反專案規範</summary>

原本的 Error enum 使用 thiserror 的 derive 巨集來產生 Display 與 Error 實作，但此 PR 移除了 thiserror 依賴，改為手動實作。這可能違反專案規範 R08（Error Types Must Use thiserror for Structured Error Handling）。若專案強制使用 thiserror，此變更應被拒絕；若允許手動實作，則需確認所有錯誤訊息與來源鏈接正確。

**判斷依據**：diff 中移除了 #[derive(Debug, thiserror::Error)]，改為 #[derive(Debug)]，並新增手動的 Display 與 Error 實作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開錯誤枚舉未標記 #[non_exhaustive]</summary>

Error enum 是公開 API，但未加上 #[non_exhaustive] 屬性。這可能違反專案規範 R09（Public Error Enums Must Be Marked as Non-Exhaustive）。若未來需要新增錯誤變體，將造成破壞性變更。建議加上 #[non_exhaustive]。

**判斷依據**：diff 中新增的 Error enum 定義沒有 #[non_exhaustive] 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 中條件判斷邏輯可能反轉</summary>

原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。這改變了當 status 為 None 時的行為：原本在 wait=false 時會進入 if 區塊，現在則在 wait=true 時才會進入。需確認此變更是否符合預期，特別是在非等待模式下是否會跳過必要的日誌輸出。

**判斷依據**：diff 中該行由 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11660 (cache hit 11648) ｜ completion tokens 797 ｜ PR #13</sub>