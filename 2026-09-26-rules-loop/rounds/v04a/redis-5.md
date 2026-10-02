<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 objectComputeSize 改名為 kvobjComputeSize，並調整記憶體計算方式，將物件標頭與嵌入的 key 納入計算，同時修正 quicklist 與 stream 的取樣平均計算。整體方向合理，但存在幾個可能導致記憶體估算錯誤或測試不穩定的問題，特別是 quicklist 取樣平均的除數錯誤、stream 的 off-by-one 修正可能重複計算，以及測試中對記憶體上限的假設過於寬鬆。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/object.c:1239` | quicklist 取樣平均計算使用錯誤的除數 | 0.90 |
| ⚠️ | Major | `src/object.c:1330` | stream 記憶體估算可能重複計算最後一個 listpack | 0.80 |
| 🔸 | Minor | `tests/unit/type/string.tcl:701` | 測試中記憶體上限假設過於寬鬆，可能無法偵測回歸 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1239</code> quicklist 取樣平均計算使用錯誤的除數</summary>

在 quicklist 的取樣計算中，原本使用 `elecount` 作為平均的除數，但此 PR 改為 `samples`。然而 `samples` 是已取樣的節點數，而 `elesize` 是這些節點中所有元素的總大小，因此平均每個元素的大小應為 `elesize / elecount`，而非 `elesize / samples`。這會導致當每個節點包含多個元素時，平均元素大小被高估，進而使整個 quicklist 的記憶體估算偏高。

**失敗情境**：建立一個包含多個元素的 quicklist（例如 list-max-listpack-size 設定較小，使每個節點包含多個元素），執行 `MEMORY USAGE` 時回報的記憶體用量會明顯高於實際。

**建議**：將除數改回 `elecount`，或明確計算每個節點的平均元素數。

**判斷依據**：diff 中此行由 `asize += (double)elesize/elecount*ql->count;` 改為 `asize += (double)elesize/samples*ql->count;`，但 `elesize` 累加的是所有取樣節點中元素的總大小，而 `samples` 是節點數，並非元素數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/object.c:1330</code> stream 記憶體估算可能重複計算最後一個 listpack</summary>

在 stream 的記憶體計算中，原本使用 `s->rax->numele-1` 來估算 listpack 的總大小，此 PR 改為 `s->rax->numele`。但程式碼後續有針對最後一個 listpack 的單獨處理（`raxSeek(&ri,"$",NULL,0);` 之後的邏輯），若 `numele` 已包含最後一個 listpack，則可能導致該 listpack 被重複計算。

**失敗情境**：當 stream 中的元素數量小於等於 sample_size 時，程式碼會進入 else 分支，此時若 `numele` 包含最後一個 listpack，則其大小會被計算兩次，導致記憶體估算偏高。

**建議**：確認 `s->rax->numele` 的定義是否包含最後一個 listpack，並相應調整計算邏輯，避免重複計算。

**判斷依據**：diff 中此行由 `asize += lpsize * (s->rax->numele-1);` 改為 `asize += lpsize * s->rax->numele;`，但後續程式碼有針對最後一個 listpack 的單獨處理，可能導致重複計算。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/string.tcl:701</code> 測試中記憶體上限假設過於寬鬆，可能無法偵測回歸</summary>

在新增的測試中，記憶體上限設定為 `max = 32 > min ? 64 : min * 2`，這允許記憶體用量高達最小值的兩倍（或至少 64 bytes）。對於較大的 key/value，實際記憶體用量通常不會達到兩倍，因此這個測試可能無法有效偵測記憶體估算的錯誤。

**失敗情境**：若程式碼錯誤地將記憶體估算為實際的 1.5 倍，此測試仍會通過，無法發現問題。

**建議**：根據實際的記憶體配置（如 jemalloc 的 size class）設定更嚴格的上限，或使用更精確的預期值。

**判斷依據**：diff 中新增的測試程式碼，此上限設定過於寬鬆，可能無法有效偵測記憶體估算錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5274 (cache hit 4736) ｜ completion tokens 1185 ｜ PR #5</sub>