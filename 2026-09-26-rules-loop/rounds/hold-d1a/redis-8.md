<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

本次 PR 修改了 hash 欄位過期（HFE）的複寫邏輯，讓 HINCRBYFLOAT 在欄位有過期時間時，以 HSET + HPEXPIREAT 的 MULTI 方式傳播，避免 replica 遺失過期時間。改動包含 src/server.c、src/server.h、src/t_hash.c 與測試檔。整體而言，程式碼結構合理，但發現一個明確的記憶體洩漏問題：在 hincrbyfloatCommand 中，手動傳播 HPEXPIREAT 時建立的 robj 陣列未釋放，違反 R02 規範。此外，測試檔中新增的測試函式未包在 REDIS_TEST 區塊內，違反 R05。建議先修正記憶體洩漏再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2309` | [R02] 記憶體洩漏：alsoPropagate 的 argv 陣列未釋放 | 0.95 |
| ⚠️ | Major | `tests/unit/type/hash-field-expire.tcl:1270` | [R05] 測試函式未包在 REDIS_TEST 區塊內 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2309</code> [R02] 記憶體洩漏：alsoPropagate 的 argv 陣列未釋放</summary>

在 `hincrbyfloatCommand` 中，當欄位有過期時間時，程式碼建立了一個 `robj *argv[5]` 陣列，並將 `argv[2]` 設為 `createStringObjectFromLongLong(expireat)`。這個新建立的 robj 在傳遞給 `alsoPropagate` 後，沒有被釋放。`alsoPropagate` 只會複製指標，不會取得所有權，因此每次執行此路徑都會洩漏一個 robj。建議在 `alsoPropagate` 呼叫後立即 `decrRefCount(argv[2])`，或改用 `addReplyArrayLen` 等不會洩漏的方式。

**判斷依據**：diff 中新增的 `createStringObjectFromLongLong` 呼叫沒有對應的 `decrRefCount`，且 `alsoPropagate` 的實作不會釋放傳入的 robj 陣列元素。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/type/hash-field-expire.tcl:1270</code> [R05] 測試函式未包在 REDIS_TEST 區塊內</summary>

新增的測試程式碼位於 `tests/unit/type/hash-field-expire.tcl`，但該檔案中的測試函式沒有被 `#ifdef REDIS_TEST` / `#endif` 包住。根據規範 R05，所有測試函式必須包在 REDIS_TEST 條件編譯區塊內，以避免測試程式碼進入 production build。請確認此測試檔案是否應被視為測試專用，若是，則需加上條件編譯保護。

**判斷依據**：diff 中新增的測試區塊沒有對應的 `#ifdef REDIS_TEST` 標記。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6046 (cache hit 5888) ｜ completion tokens 841 ｜ PR #8</sub>