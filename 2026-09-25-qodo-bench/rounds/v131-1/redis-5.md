<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，使其包含 kvobj 標頭與嵌入的 key。主要風險在於計算邏輯的變更可能導致低估或高估，特別是在 quicklist 與 stream 的取樣計算中，以及測試斷言可能過於寬鬆。建議先修正 quicklist 的取樣分母與 stream 的節點計數，並確認測試的上下界是否合理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/object.c:1239` | quicklist 取樣計算使用錯誤的分母 | 0.95 |
| ⚠️ | Major | `src/object.c:1330` | stream 記憶體估算可能重複計算最後一個節點 | 0.80 |
| ⚠️ | Major | `tests/unit/type/string.tcl:701` | 測試斷言可能過於寬鬆，無法捕捉記憶體計算錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/object.c:1239</code> quicklist 取樣計算使用錯誤的分母</summary>

在 quicklist 的記憶體估算中，原本使用 `elecount` 作為平均的分母，但此 PR 改為 `samples`。然而 `samples` 是已取樣的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會高估每個元素的平均大小，導致整體記憶體估算偏高。

**失敗情境**：建立一個包含多個元素的 quicklist，每個節點包含多個元素，呼叫 MEMORY USAGE 會得到比實際記憶體用量更高的數值。

**建議**：保留原本的 `elecount` 作為分母，或改為計算每個節點的平均元素數再乘以節點數。

**判斷依據**：diff 中將 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 `samples` 是節點數，不是元素數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 記憶體估算可能重複計算最後一個節點</summary>

在 stream 的記憶體估算中，原本使用 `s->rax->numele-1` 來計算平均 listpack 大小乘以節點數，但此 PR 改為 `s->rax->numele`。這可能導致最後一個 listpack 被重複計算，因為在取樣迴圈中已經包含了最後一個節點。

**失敗情境**：當 stream 的節點數大於 sample_size 時，最後一個節點會被包含在取樣中，然後又用 `numele` 相乘，導致高估。

**建議**：確認 `numele` 的定義是否包含最後一個節點，若包含則應維持 `-1`。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但未提供理由。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/type/string.tcl:701</code> 測試斷言可能過於寬鬆，無法捕捉記憶體計算錯誤</summary>

新增的測試使用 `assert_lessthan_equal $min $memory_used` 和 `assert_morethan_equal $max $memory_used`，其中 `max` 的計算方式為 `32 > $min ? 64 : [expr $min * 2]`。這可能允許記憶體估算有高達 2 倍的誤差，無法有效驗證計算的正確性。

**失敗情境**：如果記憶體計算錯誤導致高估 1.5 倍，測試仍會通過。

**建議**：收緊上下界，例如使用更精確的預期值或允許較小的誤差範圍。

**判斷依據**：測試中 max 的計算允許記憶體用量高達 min 的兩倍，可能掩蓋計算錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4745 (cache hit 1408) ｜ completion tokens 1047 ｜ PR #5</sub>