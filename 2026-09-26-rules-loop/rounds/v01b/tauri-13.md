<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 Tauri 專案的多個 crate 進行版本更新（patch/minor），主要內容包含：移除已完成的 change files、更新 Cargo.toml 與 Cargo.lock 的相依版本、更新 CHANGELOG、以及將 tauri-macos-sign 的 Error 型別從 thiserror 改為手動實作 Display/Error。整體風險低，但 tauri-macos-sign 的錯誤處理變更違反專案規範 R08，且公開 Error enum 未標記 #[non_exhaustive]（R09），可能造成下游 breaking change。此外，notarize_inner 中的條件判斷變更需確認邏輯正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R08] 自訂錯誤型別未使用 thiserror，違反專案規範 | 0.95 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開 Error enum 未標記 #[non_exhaustive] | 0.90 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件判斷邏輯可能反轉 | 0.80 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | 參數順序變更可能影響命令列參數語意 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R08] 自訂錯誤型別未使用 thiserror，違反專案規範</summary>

此變更將原本使用 `#[derive(Debug, thiserror::Error)]` 的 Error enum 改為手動實作 `Display` 與 `std::error::Error`。專案規範 R08 明確要求所有自訂錯誤型別必須使用 thiserror 來維持一致的錯誤處理與清晰的錯誤訊息。手動實作容易遺漏 `source()` 的正確回傳（例如 `Error::Plist` 的 `error` 欄位未回傳為 source），且未來新增 variant 時需同步修改多處，增加維護成本。建議改回使用 thiserror 並保留原有的 `#[error(...)]` 屬性。

**判斷依據**：diff 中移除了 `#[derive(Debug, thiserror::Error)]` 及所有 `#[error(...)]` 屬性，改為手動實作 `Display` 與 `Error` trait。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開 Error enum 未標記 #[non_exhaustive]</summary>

此 Error enum 為公開 API，且 changelog 中標示為 **Potentially breaking change**。若未來需要新增錯誤 variant，下游使用 exhaustive match 的程式碼將無法編譯。建議加上 `#[non_exhaustive]` 屬性，以允許向後相容地擴充錯誤型別。

**判斷依據**：diff 中新增的 `pub enum Error {` 沒有 `#[non_exhaustive]` 屬性，且 changelog 明確指出此變更為 potentially breaking。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件判斷邏輯可能反轉</summary>

原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 在 `wait` 為 true 時，若 status 為 None 會回傳 false（不進入 if），若 status 為 Some("Accepted") 則回傳 true。修改後變成 `map_or(wait, |s| s == "Accepted")`，在 `wait` 為 true 且 status 為 None 時會回傳 true，導致進入 if 區塊。這可能造成在未等待 notarization 完成時誤判為成功，進而執行後續邏輯。請確認此變更是否為預期行為，並補充測試。

**判斷依據**：diff 中此行由 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`，邏輯相反。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> 參數順序變更可能影響命令列參數語意</summary>

在 `notarize_inner` 中，`app_bundle_path` 與 `zip_path` 的參數順序被對調。若 `ditto` 命令對參數位置敏感，可能導致壓縮內容錯誤。請確認此變更是否為修正先前錯誤，並驗證產生的 zip 內容正確。

**判斷依據**：diff 中兩行參數順序互換。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12687 (cache hit 12672) ｜ completion tokens 1466 ｜ PR #13</sub>