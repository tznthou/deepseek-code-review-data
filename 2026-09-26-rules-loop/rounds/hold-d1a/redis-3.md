<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

本次 PR 主要將 cross-slot 與 no-keys 的常數從 GETSLOT_NOKEYS/GETSLOT_CROSSSLOT 改為 INVALID_CLUSTER_SLOT/CLUSTER_CROSSSLOT，並重構 extractSlotFromKeysResult 以回傳 CLUSTER_CROSSSLOT。改動中違反了 R02（使用 malloc/free 而非 zmalloc/zfree），且 extractSlotFromKeysResult 的迴圈有越界存取風險，可能導致記憶體損毀。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/cluster.c:1110` | [R02] 使用 malloc/free 而非 zmalloc/zfree | 0.95 |
| 🛑 | Blocker | `src/cluster.c:1112` | extractSlotFromKeysResult 迴圈越界寫入 | 0.95 |

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1110</code> [R02] 使用 malloc/free 而非 zmalloc/zfree</summary>

在 `extractSlotFromKeysResult` 中使用了 `malloc` 與 `free`，違反專案規範 R02（應使用 `zmalloc`/`zfree`）。此外，迴圈條件 `j <= keys_result->numkeys` 會導致越界寫入 `slot_buffer`，因為 `slot_buffer` 只配置了 `numkeys` 個元素。這可能造成記憶體損毀。建議改用 `zmalloc`/`zfree`，並將迴圈條件改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的 `malloc` 呼叫與 `j <= keys_result->numkeys` 迴圈條件。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/cluster.c:1112</code> extractSlotFromKeysResult 迴圈越界寫入</summary>

迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys`，但 `slot_buffer` 只配置了 `numkeys` 個 `int`，因此 `slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成未定義行為。應改為 `j < keys_result->numkeys`。

**判斷依據**：diff 中新增的迴圈條件。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5777 (cache hit 5632) ｜ completion tokens 613 ｜ PR #3</sub>