<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將網域暖機的郵件量限制從「依前次最高發送量乘上倍率」改為「依首次發送後經過的天數，以指數曲線從 200 成長到 200,000」。整體方向合理，但實作中有幾個關鍵問題：`getWarmupLimit` 在暖機完成後回傳 `Infinity`，可能導致呼叫端未預期的行為；`#getDaysSinceFirstEmail` 使用 `Date.now()` 而非注入的時鐘，使測試與實際行為不一致；此外，`DefaultWarmupOptions` 未凍結且型別為可變，存在被意外修改的風險。建議先處理 `Infinity` 的語意與時鐘注入問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:85` | 暖機完成後回傳 Infinity 可能導致呼叫端錯誤 | 0.90 |
| ⚠️ | Major | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:75` | 使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致 | 0.85 |
| 🔸 | Minor | `ghost/core/core/server/services/email-service/DomainWarmingService.ts:24` | DefaultWarmupOptions 未凍結且型別可變，可能被意外修改 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:85</code> 暖機完成後回傳 Infinity 可能導致呼叫端錯誤</summary>

`getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

**判斷依據**：diff 中新增的 `getWarmupLimit` 方法內，當 `day > totalDays` 時回傳 `Infinity`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:75</code> 使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致</summary>

`#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

**判斷依據**：diff 中 `#getDaysSinceFirstEmail` 方法使用 `Date.now()`，而測試檔案中使用了 `sinon.useFakeTimers`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/email-service/DomainWarmingService.ts:24</code> DefaultWarmupOptions 未凍結且型別可變，可能被意外修改</summary>

`DefaultWarmupOptions` 是一個模組層級的 `const` 物件，但內容未被凍結。任何取得參考的程式碼都可以修改其屬性，影響所有後續的服務實例。建議使用 `Object.freeze` 或將型別改為 `Readonly<WarmupVolumeOptions>`，並在建構子中複製一份。

**判斷依據**：diff 中新增的 `DefaultWarmupOptions` 常數，未使用 `Object.freeze` 或 `Readonly`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7591 (cache hit 7552) ｜ completion tokens 994 ｜ PR #9</sub>