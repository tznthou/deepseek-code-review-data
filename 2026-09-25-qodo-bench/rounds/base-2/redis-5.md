<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式：先以 malloc_usable_size 取得 kvobj 標頭大小，再累加各資料結構的配置大小。主要風險在於 quicklist 的抽樣平均計算從除以 elecount 改為除以 samples，可能導致低估或高估；stream 的 listpack 估算從乘以 (numele-1) 改為乘以 numele，可能造成高估。此外，新增的測試僅驗證記憶體使用量落在寬鬆範圍內，無法偵測精確度回歸。整體而言，變更方向合理，但需確認抽樣計算的正確性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 抽樣平均計算可能低估記憶體使用量 | 0.80 |
| ⚠️ | Major | `src/object.c:1330` | stream listpack 估算可能高估記憶體使用量 | 0.70 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 新增測試的斷言過於寬鬆，無法有效偵測記憶體計算錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 抽樣平均計算可能低估記憶體使用量</summary>

在 quicklist 的記憶體估算中，原本使用 `elesize/elecount` 來計算平均每個元素的實際大小，但此 PR 改為 `elesize/samples`。由於 `samples` 是抽樣的節點數，而 `elecount` 是抽樣節點中的元素總數，兩者通常不相等。若每個節點包含多個元素，`samples` 會小於 `elecount`，導致平均大小被高估；反之若節點數多於元素數（例如空節點），則可能低估。這會使 `MEMORY USAGE` 回報不準確的數值。建議改回使用 `elecount` 作為分母，或明確計算每個節點的平均元素數。

**判斷依據**：diff 中此行由 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 `samples` 是抽樣節點數，`elecount` 是抽樣元素總數，兩者意義不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream listpack 估算可能高估記憶體使用量</summary>

在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)` 來估算所有 listpack 的總大小，但此 PR 改為 `lpsize * s->rax->numele`。這可能導致高估，因為最後一個 listpack 可能尚未滿，且其大小可能與平均不同。原本的 `-1` 可能是為了排除最後一個 listpack 的影響，或考慮到其他因素。建議確認此變更的意圖，並確保估算值不會明顯偏離實際記憶體使用量。

**判斷依據**：diff 中此行由 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但未提供解釋為何移除 `-1`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 新增測試的斷言過於寬鬆，無法有效偵測記憶體計算錯誤</summary>

新增的 `MEMORY USAGE - STRINGS` 測試使用 `assert_lessthan_equal $min $memory_used` 和 `assert_morethan_equal $max $memory_used`，其中 `max` 是 `min` 的兩倍或 64 位元組。這種寬鬆的範圍可能無法捕捉到記憶體計算的細微錯誤，例如 quicklist 或 stream 的估算偏差。建議加入更精確的斷言，例如與已知的記憶體配置大小進行比較，或使用更嚴格的上下界。

**判斷依據**：測試中 `max` 的計算方式為 `min * 2` 或 64，這允許記憶體使用量有高達 100% 的誤差，可能無法偵測到計算錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4781 (cache hit 4736) ｜ completion tokens 1090 ｜ PR #5</sub>