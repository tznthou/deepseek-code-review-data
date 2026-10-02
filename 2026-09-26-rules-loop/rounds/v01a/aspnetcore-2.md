<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 相依版本，並包含多項建置腳本修正與測試調整。主要風險在於 `LocateVisualStudio` 函式對 `$vsRequirements` 的 null 處理邏輯變更，以及 WebSocket 測試中 `_receiveTcs` 重設時機的變動，可能影響測試可靠性。整體變更看似合理，但需確認相依版本更新後的相容性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/tools.ps1:550` | LocateVisualStudio 中 $vsRequirements 可能為 null 導致後續 Get-Member 失敗 | 0.80 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408` | WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設時機變更可能影響測試行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/tools.ps1:550</code> LocateVisualStudio 中 $vsRequirements 可能為 null 導致後續 Get-Member 失敗</summary>

在 `LocateVisualStudio` 函式中，當 `$GlobalJson.tools` 沒有 `vs` 屬性時，`$vsRequirements` 被設為 `$null`。後續的 `Get-Member -InputObject $vsRequirements -Name 'version'` 在 `$vsRequirements` 為 null 時會拋出錯誤，因為 `Get-Member` 不接受 null 輸入。雖然程式碼已加上 `$vsRequirements -and` 的條件，但條件評估順序可能導致在 `$vsRequirements` 為 null 時仍嘗試執行 `Get-Member`。建議改為先檢查 `$null -ne $vsRequirements` 再呼叫 `Get-Member`，或使用 `if ($vsRequirements -and (Get-Member -InputObject $vsRequirements -Name 'version' -ErrorAction SilentlyContinue))` 的寫法（目前已是如此，但需確認 PowerShell 版本是否支援此語法）。

**判斷依據**：diff 中新增了 `$vsRequirements = $null` 的分支，且後續的 `Get-Member` 呼叫使用了 `$vsRequirements -and` 條件。但若 `$vsRequirements` 為 null，`$vsRequirements -and (Get-Member ...)` 的評估順序可能導致 `Get-Member` 被執行（取決於 PowerShell 版本）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408</code> WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設時機變更可能影響測試行為</summary>

在 `ReceiveAsync` 方法中，`_receiveTcs` 的重設從原本在複製資料後移至 await 之後、複製資料之前。這可能導致在 zero-byte read 的情況下，`_receiveTcs` 被重設後未使用，造成後續測試行為不一致。建議確認此變更是否為了解決特定問題，並確保測試仍能正確驗證。

**判斷依據**：diff 顯示 `_receiveTcs = new(...)` 從原本在 `if (buffer.Count == 0)` 之後移至之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8709 (cache hit 6400) ｜ completion tokens 1065 ｜ PR #2</sub>