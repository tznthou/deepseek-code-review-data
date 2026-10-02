<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 修正了 HINCRBYFLOAT 在 replica 上會移除 field TTL 的問題。主要變更是將複寫指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標，同時新增了 shared objects 與測試。整體方向正確，但需注意 rewriteClientCommandVector 的參數順序、shared.fields 的長度、以及測試中對 TTL 的斷言可能過於嚴格。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | rewriteClientCommandVector 參數順序可能錯誤 | 0.80 |
| 🔸 | Minor | `src/server.c:2153` | shared.fields 字串長度可能錯誤 | 0.70 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1980` | 測試中 TTL 斷言可能過於嚴格 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> rewriteClientCommandVector 參數順序可能錯誤</summary>

在 `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，參數順序可能不正確。根據 Redis 內部慣例，HSETEX 的語法為 `HSETEX key [KEEPTTL] FIELDS num field value [field value ...]`，因此參數順序應為：指令名稱、key、KEEPTTL、FIELDS、欄位數量、欄位名稱、值。目前程式碼將 `c->argv[2]`（欄位名稱）放在 `shared.integers[1]`（數量）之後，但 `newobj`（值）放在最後，這可能導致複寫出的指令參數順序錯誤。建議確認 `rewriteClientCommandVector` 的參數順序是否正確，並調整為正確的順序。

**判斷依據**：diff 中新增的這一行，參數順序為：指令、key、keepttl、fields、數量、欄位名稱、值。但 HSETEX 的語法要求欄位名稱在值之前，因此可能導致複寫錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:2153</code> shared.fields 字串長度可能錯誤</summary>

`shared.fields = createStringObject("FIELDS",6);` 中，字串 "FIELDS" 的長度為 6，但 `createStringObject` 的第二個參數是長度，因此長度應為 6，但需確認是否正確。實際上 "FIELDS" 的長度為 6，所以此處可能正確，但需注意其他 shared object 的長度是否一致。

**判斷依據**：diff 中新增的這一行，字串長度為 6，但需確認是否與其他 shared object 的長度一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1980</code> 測試中 TTL 斷言可能過於嚴格</summary>

在測試中，`assert_range [r httl h1 FIELDS 1 f1] 90 100` 假設 TTL 在 90 到 100 秒之間，但由於測試執行時間可能超過 10 秒，TTL 可能低於 90，導致測試不穩定。建議放寬範圍或使用更精確的斷言方式。

**判斷依據**：diff 中新增的測試斷言，TTL 範圍為 90-100，但測試執行時間可能導致 TTL 低於 90。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3567 (cache hit 3456) ｜ completion tokens 973 ｜ PR #9</sub>