<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，將物件標頭與 key 的記憶體納入計算，同時修正了 quicklist 與 stream 的取樣計算。整體方向合理，但存在一些潛在問題：quicklist 的取樣計算在樣本數不足時可能低估記憶體；stream 的計算在特定條件下可能重複計算最後一個 listpack；測試中對記憶體上限的斷言可能過於寬鬆，無法有效驗證計算正確性。建議修正這些問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣計算在樣本數不足時可能低估記憶體 | 0.80 |
| ⚠️ | Major | `src/object.c:1330` | stream 記憶體計算可能重複計算最後一個 listpack | 0.70 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試中記憶體上限斷言過於寬鬆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣計算在樣本數不足時可能低估記憶體</summary>

在 quicklist 的計算中，原本使用 `elesize/elecount*ql->count` 來估算總元素大小，現在改為 `elesize/samples*ql->count`。當 quicklist 的節點數少於 sample_size 時，samples 會小於 elecount，導致平均元素大小被高估，進而高估總記憶體。反之，若節點數多於 sample_size，samples 等於 sample_size，此時使用 samples 作為分母是正確的。但當節點數少於 sample_size 時，應使用 elecount 作為分母，否則會高估記憶體。建議改為 `elesize/elecount*ql->count`，或根據實際樣本數動態選擇分母。

**判斷依據**：diff 中此行由 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 samples 在迴圈中遞增，若 quicklist 節點數少於 sample_size，samples 會小於 elecount，導致平均元素大小被高估。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 記憶體計算可能重複計算最後一個 listpack</summary>

在 stream 的計算中，原本使用 `lpsize * (s->rax->numele-1)` 來估算除了最後一個 listpack 之外的總大小，現在改為 `lpsize * s->rax->numele`。但後續程式碼會單獨處理最後一個 listpack（透過 `raxSeek(&ri,"$",NULL,0)` 取得並加入其大小），若將 numele 全部乘上平均大小，會重複計算最後一個 listpack。建議改回 `lpsize * (s->rax->numele-1)`，或調整後續邏輯避免重複。

**判斷依據**：diff 中此行由 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但下方仍有處理最後一個 listpack 的程式碼，可能導致重複計算。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試中記憶體上限斷言過於寬鬆</summary>

測試中對 memory usage 的上限使用 `assert_morethan_equal $max $memory_used`，其中 `max` 為 `min` 的兩倍或 64。這可能無法有效驗證計算的準確性，因為即使計算有誤差，只要不超過兩倍就能通過。建議根據實際記憶體配置設定更嚴格的上限，或使用更精確的預期值。

**判斷依據**：測試中設定的上限為 min 的兩倍或 64，過於寬鬆，可能無法捕捉記憶體計算的錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4745 (cache hit 4736) ｜ completion tokens 1045 ｜ PR #5</sub>