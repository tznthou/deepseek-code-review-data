<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題。主要變更包括：在 hashTypeGetValue 增加 expiredAt 輸出參數、在 hincrbyfloatCommand 中偵測過期時間並手動傳播 HSET 與 HPEXPIREAT、新增 shared.fields 物件、以及新增測試。整體方向正確，但存在一個嚴重的記憶體洩漏：在傳播 HPEXPIREAT 時建立的 argv[2] 字串物件未釋放，可能導致長期記憶體成長。此外，測試中使用了未定義的變數 h1，可能導致測試失敗或誤判。建議先修正記憶體洩漏與測試變數問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2309` | HPEXPIREAT 傳播時建立的 argv[2] 字串物件未釋放，造成記憶體洩漏 | 0.95 |
| ⚠️ | Major | `tests/unit/type/hash-field-expire.tcl:1179` | 測試中使用了未定義的變數 h1 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2309</code> HPEXPIREAT 傳播時建立的 argv[2] 字串物件未釋放，造成記憶體洩漏</summary>

在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);` 並傳遞給 `alsoPropagate`。但 `alsoPropagate` 不會取得物件的所有權，呼叫後此物件不會被釋放。每次執行具有過期時間的 HINCRBYFLOAT 都會洩漏一個 robj，長期下來可能導致記憶體耗盡。

建議在 `alsoPropagate` 呼叫後立即 `decrRefCount(argv[2]);`，或改用其他方式建立暫時物件（例如使用 stack 上的 robj 或直接傳遞字串）。

**判斷依據**：diff 中新增的程式碼片段顯示 `argv[2]` 由 `createStringObjectFromLongLong` 建立，但後續沒有對應的 `decrRefCount`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/type/hash-field-expire.tcl:1179</code> 測試中使用了未定義的變數 h1</summary>

在測試 `HINCRBYFLOAT command won't remove field expiration on replica ($type)` 中，使用了變數 `h1`，但在此測試的 scope 內並未定義。這可能導致 Tcl 錯誤或測試意外通過/失敗。

請確認 `h1` 是否應為某個先前定義的變數，或改為明確的 key 名稱（例如 `myhash`）。

**判斷依據**：diff 中新增的測試程式碼直接使用 `h1`，但未見其定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13233 (cache hit 1536) ｜ completion tokens 826 ｜ PR #8</sub>