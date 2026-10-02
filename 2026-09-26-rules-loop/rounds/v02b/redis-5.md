<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式：先以 malloc_usable_size 取得物件整體配置大小，再依類型加上額外配置。主要風險在於 stream 的取樣計算從 (numele-1) 改為 numele，可能高估記憶體；且新增的測試僅以寬鬆上下界驗證，無法偵測此類誤差。建議先確認 stream 計算邏輯，並考慮加入更精確的測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1330` | Stream 記憶體估算可能高估：取樣平均乘以 numele 而非 (numele-1) | 0.80 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 新增測試的記憶體上限過於寬鬆，可能無法偵測高估 | 0.70 |
| 🔸 | Minor | `src/object.c:1239` | 取樣平均計算使用 samples 而非 elecount，可能低估平均元素大小 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> Stream 記憶體估算可能高估：取樣平均乘以 numele 而非 (numele-1)</summary>

在 stream 的記憶體估算中，原本使用 `s->rax->numele-1` 作為乘數，此 PR 改為 `s->rax->numele`。若 `numele` 包含 radix tree 的 header 節點，則此變更會將 header 節點也納入平均計算，導致高估記憶體使用量。建議確認 `numele` 的定義，若確實包含 header，應保留 `-1` 或調整取樣邏輯。

**判斷依據**：diff 中將 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，且上下文顯示此處為 stream 的 listpack 平均大小計算。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 新增測試的記憶體上限過於寬鬆，可能無法偵測高估</summary>

測試中 `max` 的計算為 `32 > $min ? 64 : $min * 2`，當 `min` 較大時，上限為 `min` 的兩倍，可能無法偵測到記憶體估算的顯著高估。建議根據實際配置大小設定更嚴格的上限，或使用 jemalloc 的統計資訊進行驗證。

**判斷依據**：diff 中新增的測試程式碼包含此上限計算，且測試目的為驗證 kvobjComputeSize 的正確性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1239</code> 取樣平均計算使用 samples 而非 elecount，可能低估平均元素大小</summary>

在 quicklist 的計算中，原本使用 `elecount` 作為平均的分母，此 PR 改為 `samples`。若 `samples` 代表取樣的節點數，而 `elecount` 代表取樣節點中的元素總數，則當節點內元素數不固定時，使用 `samples` 會低估平均元素大小。建議確認 `samples` 與 `elecount` 的語意，若 `samples` 為節點數，應保留 `elecount` 作為分母。

**判斷依據**：diff 中將 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，且上下文顯示 `samples` 為取樣節點數，`elecount` 為取樣元素總數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5782 (cache hit 5760) ｜ completion tokens 936 ｜ PR #5</sub>