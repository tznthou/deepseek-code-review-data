<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式：將物件標頭與 key 的記憶體納入計算，並修正 quicklist 與 stream 的取樣平均計算。整體方向合理，但存在一個可能導致記憶體估算錯誤的邏輯變更（quicklist 平均計算），以及測試中對記憶體上限的斷言過於寬鬆，可能無法有效驗證。建議修正 quicklist 計算並強化測試斷言。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 記憶體估算的平均計算可能錯誤 | 0.80 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試斷言過於寬鬆，可能無法有效驗證記憶體計算 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 記憶體估算的平均計算可能錯誤</summary>

在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count` 來計算平均每個元素的記憶體，但此 PR 改為 `elesize/samples*ql->count`。然而 `samples` 是取樣節點數，而 `elesize` 是這些節點中所有元素的總記憶體，因此 `elesize/samples` 得到的是每個節點的平均記憶體，而非每個元素的平均記憶體。這會導致當節點內元素數量不固定時，估算結果不準確。

**失敗情境**：假設 quicklist 有 10 個節點，每個節點包含 100 個元素，每個元素佔 10 bytes。取樣 5 個節點，則 `elesize` = 5 * 100 * 10 = 5000，`samples` = 5，`elesize/samples` = 1000，再乘以 `ql->count` (1000) 得到 1,000,000 bytes，但實際記憶體約為 10 * 1000 = 10,000 bytes（不計節點開銷），嚴重高估。

**建議**：改回使用 `elecount` 作為分母，或確保 `elesize` 是每個元素的平均記憶體。

**判斷依據**：diff 中將 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 `elesize` 是累加所有取樣節點中元素的記憶體，而 `samples` 是節點數，非元素數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試斷言過於寬鬆，可能無法有效驗證記憶體計算</summary>

在新增的 MEMORY USAGE 測試中，對記憶體上限的斷言使用 `assert_morethan_equal $max $memory_used`，其中 `max` 的計算為 `32 > $min ? 64 : [expr $min * 2]`。這表示允許記憶體使用量高達最小值的兩倍（或至少 64 bytes），這可能過於寬鬆，無法捕捉到明顯的記憶體高估錯誤。

**失敗情境**：如果程式碼錯誤地將每個 key 的記憶體計算為實際的 1.5 倍，此測試仍會通過，因為 1.5 倍小於 2 倍。

**建議**：考慮使用更嚴格的上限，例如 `$min + 固定開銷` 或基於實際配置的合理範圍，以增加測試的敏感度。

**判斷依據**：測試中對 `max` 的計算方式過於寬鬆，可能無法有效驗證記憶體計算的正確性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5772 (cache hit 5760) ｜ completion tokens 925 ｜ PR #5</sub>