<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要更新 dotnet/arcade 依賴版本，並包含多項基礎架構調整：Azure Linux 3 映像、來源索引條件、內部來源 URL、PowerShell 下載參數、Visual Studio 偵測邏輯，以及測試相關變更（WebSocket 壓縮測試的錯誤訊息正規化、Redis 測試的隔離與順序調整）。整體風險中等，需特別注意 `LocateVisualStudio` 中 `$vsRequirements` 可能為 `$null` 的處理，以及 `WebSocketWrapper.ReceiveAsync` 中 `_receiveTcs` 重設時機的變更是否會影響測試行為。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `eng/common/tools.ps1:550` | `$vsRequirements` 可能為 `$null`，後續成員存取可能拋出例外 | 0.80 |
| 🔸 | Minor | `src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408` | `_receiveTcs` 重設時機變更可能影響測試行為 | 0.60 |
| 🔸 | Minor | `src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107` | 測試斷言使用 `Assert.True` 搭配兩個 Regex 的 AND 條件，可能降低可讀性 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>eng/common/tools.ps1:550</code> `$vsRequirements` 可能為 `$null`，後續成員存取可能拋出例外</summary>

在 `LocateVisualStudio` 函式中，當 `$GlobalJson.tools` 沒有 `vs` 屬性時，`$vsRequirements` 會被設為 `$null`。後續的 `if ($vsRequirements -and (Get-Member -InputObject $vsRequirements -Name 'version' ...))` 已加上 `$vsRequirements -and` 條件，但接下來的 `if ($vsRequirements -and (Get-Member -InputObject $vsRequirements -Name 'components' ...))` 也同樣有保護。然而，在 `if (!$vsRequirements) { ... }` 區塊之後，程式碼直接使用 `$vsRequirements` 作為 `Get-Member` 的 `-InputObject`，若 `$vsRequirements` 為 `$null`，`Get-Member` 會拋出「Cannot bind argument to parameter 'InputObject' because it is null」的錯誤。建議在呼叫 `Get-Member` 前先檢查 `$vsRequirements` 是否為 `$null`，或使用 `-ErrorAction SilentlyContinue` 並搭配條件判斷。

**判斷依據**：diff 中新增了 `$vsRequirements = $null` 的分支，但後續的 `Get-Member` 呼叫未對 `$null` 進行防護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408</code> `_receiveTcs` 重設時機變更可能影響測試行為</summary>

在 `WebSocketWrapper.ReceiveAsync` 中，原本在處理零位元組讀取後才重設 `_receiveTcs`，現在改為在 await 後立即重設。這可能導致在零位元組讀取時，新的 `_receiveTcs` 被建立，但後續的 `SetReceiveResult` 可能設定到新的 TCS 上，而測試預期的是舊的 TCS。需要確認此變更是否會造成測試不穩定或失敗。

**判斷依據**：diff 顯示 `_receiveTcs = new(...)` 從零位元組檢查之後移到之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107</code> 測試斷言使用 `Assert.True` 搭配兩個 Regex 的 AND 條件，可能降低可讀性</summary>

原本使用 `Assert.Matches` 檢查單一 Regex，現在改為 `Assert.True` 並同時檢查兩個 Regex 是否都匹配。這可能導致當訊息只符合其中一個 Regex 時，錯誤訊息不夠明確。建議改用 `Assert.Matches` 分別檢查，或使用 `Assert.True` 時提供更詳細的失敗訊息。

**判斷依據**：diff 顯示測試斷言從 `Assert.Matches` 改為 `Assert.True` 並結合兩個 Regex。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6524 (cache hit 1536) ｜ completion tokens 1394 ｜ PR #2</sub>