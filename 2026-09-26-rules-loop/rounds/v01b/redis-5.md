<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，使其包含 kvobj header 與 embedded key 的大小。主要風險在於計算邏輯的變更可能導致記憶體估算不準確，尤其是 quicklist 與 stream 的樣本平均計算方式改變，以及 OBJ_ENCODING_INT 與 EMBSTR 的處理方式。此外，測試中對 memory usage 的上下界假設可能過於寬鬆，無法有效驗證正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 記憶體估算使用 samples 而非 elecount 可能導致不準確 | 0.80 |
| ⚠️ | Major | `src/object.c:1330` | stream 記憶體估算中 lpsize 乘以 numele 可能多算最後一個 listpack | 0.70 |
| 🔸 | Minor | `src/object.c:1217` | OBJ_ENCODING_INT 與 EMBSTR 的記憶體計算可能重複計算 header | 0.60 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試中 memory usage 的上界過於寬鬆，可能無法偵測錯誤 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 記憶體估算使用 samples 而非 elecount 可能導致不準確</summary>

在 quicklist 的計算中，原本使用 `(double)elesize/elecount*ql->count`，現在改為 `(double)elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點的元素數不同（例如 quicklist 節點可能包含多個元素），使用 `samples` 作為分母會高估或低估每個元素的平均大小，導致最終估算偏差。建議改回使用 `elecount` 作為分母，或確認 quicklist 節點數與元素數的關係。

**判斷依據**：diff 中將 `(double)elesize/elecount*ql->count` 改為 `(double)elesize/samples*ql->count`，但 `samples` 是節點數，`elecount` 是元素數，兩者可能不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 記憶體估算中 lpsize 乘以 numele 可能多算最後一個 listpack</summary>

在 stream 的計算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。註解提到最後一個 listpack 通常非滿，因此先前減去 1 是為了避免高估。現在直接乘以 `numele` 可能導致高估記憶體使用量。建議確認此變更是否為預期，或保留原本的 `-1`。

**判斷依據**：diff 中將 `lpsize * (s->rax->numele-1)` 改為 `lpsize * s->rax->numele`，但註解說明最後一個 listpack 通常非滿。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/object.c:1217</code> OBJ_ENCODING_INT 與 EMBSTR 的記憶體計算可能重複計算 header</summary>

在 OBJ_STRING 的處理中，OBJ_ENCODING_INT 與 OBJ_ENCODING_EMBSTR 的分支現在不增加 `asize`，因為註解說 value 已包含在 header 中。但 `asize` 初始值為 `malloc_usable_size((void *)o)`，這可能已包含 header 和 value 的配置大小。若 `malloc_usable_size` 回傳的空間包含整個配置區塊，則可能重複計算。建議確認 `malloc_usable_size` 的語意，並確保沒有重複計算。

**判斷依據**：diff 中新增 `size_t asize = malloc_usable_size((void *)o);`，且後續 INT/EMBSTR 分支不再增加大小。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試中 memory usage 的上界過於寬鬆，可能無法偵測錯誤</summary>

測試中設定 `max` 為 `32 > $min ? 64 : [expr $min * 2]`，這允許記憶體使用量高達最小值的兩倍或 64 bytes。這樣的寬鬆範圍可能無法有效驗證記憶體計算的正確性，尤其是當計算錯誤導致高估時。建議縮小上界，或使用更精確的預期值。

**判斷依據**：diff 中新增此測試，上界設定寬鬆。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5782 (cache hit 5760) ｜ completion tokens 1179 ｜ PR #5</sub>