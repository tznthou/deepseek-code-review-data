<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複本上會移除欄位 TTL 的問題，改為複寫成 HSETEX KEEPTTL 指令。主要風險在於複寫指令的建構方式、共享物件生命週期，以及測試對 TTL 的斷言可能不穩定。建議先確認 rewriteClientCommandVector 的參數正確性與 shared 物件的引用計數。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | 複寫指令參數順序可能錯誤 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:2571` | 共享物件引用計數可能不正確 | 0.70 |
| 🔸 | Minor | `src/t_hash.c:2571` | 複寫指令參數個數可能錯誤 | 0.60 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1981` | 測試中 TTL 斷言可能不穩定 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> 複寫指令參數順序可能錯誤</summary>

`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 建構的指令為 `HSETEX key KEEPTTL FIELDS 1 field value`。但根據 Redis 命令語法，HSETEX 的格式應為 `HSETEX key [NX|XX] [KEEPTTL] [FIELDS numfields field value ...]`，KEEPTTL 應在 FIELDS 之前。目前順序會導致命令解析錯誤，複本執行失敗。建議調整為 `rewriteClientCommandVector(c, 7, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 並確認參數個數。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫，參數順序為 hsetex, key, keepttl, fields, 1, field, value。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> 共享物件引用計數可能不正確</summary>

`rewriteClientCommandVector` 會增加傳入 robj 的引用計數，但 `shared.keepttl`、`shared.fields`、`shared.integers[1]` 是共享物件，其引用計數可能被錯誤管理。若函式內部對這些物件進行 decrRefCount，可能導致共享物件被釋放或計數失衡。建議確認 rewriteClientCommandVector 的實作，或改用非共享的 robj。

**判斷依據**：使用 shared.keepttl、shared.fields、shared.integers[1] 作為參數傳遞給 rewriteClientCommandVector。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2571</code> 複寫指令參數個數可能錯誤</summary>

`rewriteClientCommandVector` 的第二個參數為 6，但實際傳入的 robj 指標有 7 個（hsetex, key, keepttl, fields, 1, field, value）。若函式依賴此參數決定陣列長度，可能導致記憶體越界或參數遺失。建議確認函式簽名與參數個數。

**判斷依據**：參數個數 6 與實際傳入的 7 個 robj 不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1981</code> 測試中 TTL 斷言可能不穩定</summary>

`assert_range [r httl h1 FIELDS 1 f1] 90 100` 假設 TTL 在 90 到 100 秒之間，但測試執行時間可能超過 10 秒，導致 TTL 低於 90 而失敗。建議放寬範圍或使用更精確的同步機制。

**判斷依據**：測試中對 TTL 的範圍斷言，未考慮執行時間延遲。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4604 (cache hit 1536) ｜ completion tokens 1183 ｜ PR #9</sub>