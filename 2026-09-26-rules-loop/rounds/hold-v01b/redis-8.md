<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在 replica 上會移除 field expiration 的問題。主要變更在 t_hash.c 中修改 hashTypeGetValue 的簽名以輸出過期時間，並在 hincrbyfloatCommand 中手動傳播 HSET 與 HPEXPIREAT。整體方向正確，但存在一個嚴重的陣列越界錯誤（argv[5] 超出宣告大小），可能導致記憶體損壞。此外，測試中對 replication stream 的順序假設可能不穩定，且新增的 shared.fields 物件未在共享物件初始化中檢查記憶體分配失敗。建議修正陣列大小後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2306` | 陣列越界：argv 宣告大小為 5，但存取 argv[5] | 0.99 |
| ⚠️ | Major | `src/t_hash.c:2309` | 記憶體洩漏：createStringObjectFromLongLong 建立的物件未釋放 | 0.80 |
| 🔸 | Minor | `src/server.c:1990` | shared.fields 初始化未檢查記憶體分配失敗 | 0.60 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1282` | 測試中 replication stream 順序假設可能不穩定 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2306</code> 陣列越界：argv 宣告大小為 5，但存取 argv[5]</summary>

在 hincrbyfloatCommand 中，`robj *argv[5];` 宣告了大小為 5 的陣列，但後續指派了 6 個元素（argv[0] 到 argv[5]），導致寫入超出陣列邊界。這會造成 stack buffer overflow，可能導致程式崩潰或安全漏洞。

建議將陣列大小改為 6：`robj *argv[6];`

**判斷依據**：diff 中新增的程式碼片段顯示 `robj *argv[5];` 但隨後指派了 6 個元素，最後一個是 `argv[5] = c->argv[2];`，明顯越界。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2309</code> 記憶體洩漏：createStringObjectFromLongLong 建立的物件未釋放</summary>

在傳播 HPEXPIREAT 時，`argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 `alsoPropagate` 之後沒有對其進行 `decrRefCount`。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。

建議在 `alsoPropagate` 呼叫後加入 `decrRefCount(argv[2]);` 或使用 stack 分配的 robj 並設定 refcount。

**判斷依據**：diff 中顯示 `createStringObjectFromLongLong` 的回傳值被直接放入 argv[2]，但沒有對應的 `decrRefCount`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:1990</code> shared.fields 初始化未檢查記憶體分配失敗</summary>

`shared.fields = createStringObject("FIELDS",6);` 直接指派，未檢查 `createStringObject` 是否可能回傳 NULL（在記憶體不足時）。雖然 Redis 通常會 abort，但其他 shared 物件初始化也未檢查，因此這可能符合既有慣例。建議確認是否需要處理。

**判斷依據**：diff 中新增的這一行沒有錯誤處理，但與其他 shared 物件初始化方式一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1282</code> 測試中 replication stream 順序假設可能不穩定</summary>

測試使用 `assert_replication_stream` 檢查 replication stream 的內容，但假設了特定的命令順序（HSET 後接 HPEXPIREAT 等）。在實際執行中，命令的傳播順序可能受到其他因素影響（如非同步處理），導致測試偶發性失敗。建議改用更穩健的驗證方式，例如直接檢查 replica 上的資料狀態。

**判斷依據**：測試中對 replication stream 的嚴格順序檢查可能受到 Redis 內部傳播時序的影響。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6009 (cache hit 5888) ｜ completion tokens 1337 ｜ PR #8</sub>