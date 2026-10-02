<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複製時會移除欄位 TTL 的問題，改以 HSETEX KEEPTTL 複製。主要變更在 t_hash.c 的複製邏輯，並新增 shared objects 與測試。整體方向正確，但需注意 rewriteClientCommandVector 的參數順序與 shared.integers[1] 的使用，以及測試中 TTL 範圍斷言可能過於嚴格。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數順序可能錯誤 | 0.80 |
| 🔸 | Minor | `src/t_hash.c:2572` | shared.integers[1] 的使用可能造成混淆 | 0.60 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:2000` | 測試中 TTL 範圍斷言可能過於嚴格 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數順序可能錯誤</summary>

在 `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，參數順序可能與預期不符。根據 Redis 內部慣例，`rewriteClientCommandVector` 的參數應為 (client, argc, ...argv)，但此處傳入的 `shared.integers[1]` 可能代表數字 1，而 `c->argv[2]` 是欄位名稱。若順序錯誤，複製到 replica 的指令可能變成 `HSETEX key KEEPTTL FIELDS 1 field value`，但實際可能被解讀為 `HSETEX key KEEPTTL FIELDS field 1 value`，導致語法錯誤或行為異常。建議確認 `rewriteClientCommandVector` 的實作與其他呼叫點，確保參數順序正確。

**判斷依據**：diff 中新增的這一行，與常見的 rewriteClientCommandVector 用法不同，且 shared.integers[1] 是整數 1 的 shared object，可能被誤用為欄位數量。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2572</code> shared.integers[1] 的使用可能造成混淆</summary>

使用 `shared.integers[1]` 來表示欄位數量 1，雖然可行，但可讀性較差。建議改用明確的常數或建立專用的 shared object，例如 `shared.one`，以避免未來維護時誤解。

**判斷依據**：diff 中出現 `shared.integers[1]`，但此陣列通常用於整數共享物件，直接使用索引 1 可能讓讀者困惑。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:2000</code> 測試中 TTL 範圍斷言可能過於嚴格</summary>

在測試中，使用 `assert_range [r httl h1 FIELDS 1 f1] 90 100` 來驗證 TTL 範圍。由於測試執行時間可能因環境而異，TTL 可能略低於 90 毫秒，導致測試不穩定。建議放寬範圍或使用更精確的同步機制。

**判斷依據**：diff 中新增的測試斷言，TTL 範圍為 90 到 100，但實際 TTL 可能因延遲而低於 90。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13129 (cache hit 13056) ｜ completion tokens 927 ｜ PR #9</sub>