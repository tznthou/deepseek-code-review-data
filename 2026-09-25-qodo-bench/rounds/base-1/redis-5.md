<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，使其包含 kvobj header 與 embedded key 的大小。主要風險在於計算方式變更可能導致記憶體估算不準確，尤其是 quicklist 與 stream 的取樣計算，以及測試中 max 上限的設定可能過於寬鬆，無法有效驗證。建議先修正 quicklist 的取樣計算與 stream 的 lpsize 計算，並重新檢視測試的斷言。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差 | 0.80 |
| ⚠️ | Major | `src/object.c:1330` | stream 的 lpsize 計算可能多算最後一個 listpack | 0.70 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試中 max 上限設定過於寬鬆，可能無法有效驗證記憶體估算 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差</summary>

在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

**判斷依據**：diff 中將 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 `samples` 是節點數而非元素數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 的 lpsize 計算可能多算最後一個 listpack</summary>

在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。若 `lpsize` 是平均每個 listpack 的大小，且最後一個 listpack 可能未滿，則乘以 `numele` 會高估記憶體。建議確認此變更是否正確，或保留原本的 `-1`。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試中 max 上限設定過於寬鬆，可能無法有效驗證記憶體估算</summary>

在新增的測試中，`max` 設定為 `32 > $min ? 64 : [expr $min * 2]`。當 `min` 大於 32 時，上限為 `min * 2`，這可能過於寬鬆，無法偵測記憶體估算的顯著偏差。建議設定更嚴格的上限，例如 `min + 固定值` 或 `min * 1.5`。

**判斷依據**：測試中新增的斷言使用寬鬆的上限，可能無法有效驗證記憶體計算的正確性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4781 (cache hit 1536) ｜ completion tokens 898 ｜ PR #5</sub>