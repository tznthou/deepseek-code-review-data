<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為版本更新與相依性升級，主要包含：移除兩個 change files、更新多個 crate 版本號、將 tauri-macos-sign 的 Error 從 thiserror 改為手動實作 Display/Error，以及修正 notarize_inner 中的引數順序與條件判斷。風險集中在 Error 手動實作可能遺漏 source() 或格式不一致，以及 notarize_inner 的邏輯變更是否正確。建議優先確認 Error 實作與 notarize_inner 的修正。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:20` | [R08] 手動實作 Error 取代 thiserror，可能遺漏 source() 或格式不一致 | 0.80 |
| ⚠️ | Major | `crates/tauri-macos-sign/src/lib.rs:233` | notarize_inner 條件判斷邏輯變更可能導致非預期行為 | 0.70 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:173` | 引數順序調整可能影響命令列工具行為 | 0.60 |
| 🔸 | Minor | `crates/tauri-macos-sign/src/lib.rs:21` | [R09] 公開 Error enum 未標記 #[non_exhaustive] | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:20</code> [R08] 手動實作 Error 取代 thiserror，可能遺漏 source() 或格式不一致</summary>

此變更將原本使用 thiserror 的 Error enum 改為手動實作 Display 與 Error。手動實作容易出錯，例如 source() 方法中未包含所有帶有來源錯誤的變體（如 Plist、X509Certificate、FailedToCreateSelfSignedCertificate、FailedToEncodeDER 等），這會導致錯誤鏈不完整，影響除錯與下游處理。建議改回使用 thiserror，或補齊所有 source() 的對應。

**判斷依據**：diff 中移除了 #[derive(Debug, thiserror::Error)] 與所有 #[error(...)] 屬性，改為手動實作 Display 與 Error。手動實作的 source() 僅回傳 TempDir、FailedToUploadApp、CommandFailed、Fs 的來源，其他變體未處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>crates/tauri-macos-sign/src/lib.rs:233</code> notarize_inner 條件判斷邏輯變更可能導致非預期行為</summary>

原本 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。此變更會影響在 status 為 None 時的行為：原本當 wait=false 時會進入 if 區塊，現在則變成 wait=true 時才會進入。需確認此修正是否符合預期，並檢查是否可能導致在非等待模式下跳過必要的處理。

**判斷依據**：diff 中該行由 `map_or(!wait, ...)` 改為 `map_or(wait, ...)`，且前後文顯示此條件控制是否列印 notarizing 訊息與後續等待邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:173</code> 引數順序調整可能影響命令列工具行為</summary>

在 notarize_inner 中，`app_bundle_path` 與 `zip_path` 的引數順序被對調。若此命令列工具的參數位置有特定意義，可能導致行為錯誤。需確認 ditto 或後續命令的參數順序是否正確。

**判斷依據**：diff 顯示原本 app_bundle_path 在前，zip_path 在後，現在順序相反。

</details>

<details><summary>🔸 <b>Minor</b> — <code>crates/tauri-macos-sign/src/lib.rs:21</code> [R09] 公開 Error enum 未標記 #[non_exhaustive]</summary>

此 Error enum 為公開 API，且未來可能新增變體。建議加上 #[non_exhaustive] 以避免下游 match 時因新增變體而破壞。

**判斷依據**：diff 中 Error enum 為公開，且未見 #[non_exhaustive] 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12687 (cache hit 1536) ｜ completion tokens 1076 ｜ PR #13</sub>