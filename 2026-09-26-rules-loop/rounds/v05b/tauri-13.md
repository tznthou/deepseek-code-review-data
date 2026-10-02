<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新，主要將多個 crate 從 2.9.0 升級至 2.9.1（tauri-macos-sign 為 2.3.0），並包含 tauri-macos-sign 的錯誤類型重構：移除 thiserror 改用手動實作 Display/Error，以及修正 notarize_inner 中的條件判斷。整體風險集中在 tauri-macos-sign 的變更：手動實作錯誤處理可能違反專案規範 R08，且條件判斷的修改需要確認邏輯正確性。建議先確認這些變更的意圖與測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R08] 錯誤類型未使用 thiserror，違反專案規範 | 0.90 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件判斷邏輯可能反轉 | 0.80 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開錯誤枚舉未標記 #[non_exhaustive] | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R08] 錯誤類型未使用 thiserror，違反專案規範</summary>

此 PR 將原本使用 `#[derive(Debug, thiserror::Error)]` 的 `Error` enum 改為手動實作 `Display` 和 `std::error::Error`。專案規範 R08 明確要求所有自訂錯誤類型使用 thiserror 以維持一致的錯誤處理。手動實作可能導致錯誤訊息不一致、增加維護成本，且違反專案慣例。建議改回使用 thiserror，或提供充分理由說明為何需要手動實作。

**判斷依據**：diff 中刪除了 `#[derive(Debug, thiserror::Error)]` 及所有 `#[error(...)]` 屬性，並新增了 `impl std::fmt::Display for Error` 和 `impl std::error::Error for Error`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件判斷邏輯可能反轉</summary>

原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。此變更將 `map_or` 的預設值從 `!wait` 改為 `wait`，可能改變行為。需要確認：當 `status` 為 `None` 時，原本在 `wait=false` 時會進入 if 區塊，現在則在 `wait=true` 時進入。若此變更非預期，可能導致 notarization 流程錯誤。建議確認此修改的意圖，並補充測試。

**判斷依據**：diff 中該行從 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開錯誤枚舉未標記 #[non_exhaustive]</summary>

`Error` enum 是公開 API，且此 PR 將其從 thiserror 改為手動實作，但未加上 `#[non_exhaustive]`。專案規範 R09 建議公開錯誤枚舉應標記為 non-exhaustive 以避免未來新增 variant 造成 breaking change。建議加上 `#[non_exhaustive]`。

**判斷依據**：diff 中 `Error` enum 定義沒有 `#[non_exhaustive]` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12615 (cache hit 12544) ｜ completion tokens 896 ｜ PR #13</sub>