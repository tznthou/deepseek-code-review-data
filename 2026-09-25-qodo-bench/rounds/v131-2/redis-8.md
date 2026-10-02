<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在複本上會移除欄位過期時間的問題。主要變更包括：hashTypeGetValue 新增 expiredAt 輸出參數、hincrbyfloatCommand 在欄位有過期時間時手動傳播 HSET 與 HPEXPIREAT、新增 shared.fields 共用物件，以及新增測試。整體方向正確，但存在一個嚴重的記憶體洩漏：手動傳播 HPEXPIREAT 時建立的 expireat 字串物件未釋放，可能導致長期記憶體成長。此外，測試中對複本執行 HINCRBYFLOAT 的預期行為驗證不足，且部分程式碼風格與既有慣例不一致。建議先修正記憶體洩漏再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2309` | 手動傳播 HPEXPIREAT 時建立的 expireat 字串物件未釋放，造成記憶體洩漏 | 0.95 |
| ⚠️ | Major | `src/t_hash.c:2306` | 手動傳播 HPEXPIREAT 時使用未初始化的 argv 陣列大小 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:2309` | 手動傳播 HPEXPIREAT 時 expireat 的型別轉換可能導致溢位 | 0.75 |
| 🔸 | Minor | `src/t_hash.c:2313` | 手動傳播 HPEXPIREAT 時未檢查 alsoPropagate 的返回值 | 0.70 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1314` | 測試未驗證複本上 HINCRBYFLOAT 的實際值 | 0.65 |
| 🔹 | Nit | `src/t_hash.c:2244` | 變數命名 unused_flag 可能造成混淆 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2309</code> 手動傳播 HPEXPIREAT 時建立的 expireat 字串物件未釋放，造成記憶體洩漏</summary>

在 `hincrbyfloatCommand` 中，當欄位有過期時間時，會建立一個新的 robj 來存放 expireat 的十進位字串：
```c
argv[2] = createStringObjectFromLongLong(expireat);
```
此物件被放入 `argv` 陣列並傳遞給 `alsoPropagate`，但之後沒有對其呼叫 `decrRefCount`。`alsoPropagate` 會複製參數（透過 `propagate` 內部機制），不會取得傳入物件的所有權，因此呼叫者必須負責釋放。這會導致每次執行帶有過期時間的 HINCRBYFLOAT 時洩漏一個 robj，長期下來可能造成記憶體耗盡。

**失敗情境**：在一個迴圈中對具有過期時間的欄位執行 HINCRBYFLOAT，每次迭代都會洩漏一個 robj，最終導致 Redis 程序記憶體使用量持續上升。

**建議修法**：在 `alsoPropagate` 呼叫之後，立即釋放該物件：
```c
decrRefCount(argv[2]);
```
或者，如果 `alsoPropagate` 會複製參數，則可以在建立後立即釋放，但需確認 `alsoPropagate` 的實作。

**判斷依據**：diff 中新增的程式碼片段：
```c
+        robj *argv[5];
+        argv[0] = shared.hpexpireat;
+        argv[1] = c->argv[1];
+        argv[2] = createStringObjectFromLongLong(expireat);
+        argv[3] = shared.fields;
+        argv[4] = shared.integers[1];
+        argv[5] = c->argv[2];
+        alsoPropagate(c->db->id, argv, 6, PROPAGATE_AOF|PROPAGATE_REPL);
```
沒有對 `argv[2]` 呼叫 `decrRefCount`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2306</code> 手動傳播 HPEXPIREAT 時使用未初始化的 argv 陣列大小</summary>

在 `hincrbyfloatCommand` 中，宣告了 `robj *argv[5];`，但實際上使用了 6 個元素（索引 0 到 5）。這會導致陣列越界寫入，屬於未定義行為，可能造成記憶體損壞或安全漏洞。

**失敗情境**：當執行帶有過期時間的 HINCRBYFLOAT 時，寫入 `argv[5]` 會超出陣列邊界，可能覆蓋堆疊上的其他變數，導致程式崩潰或被利用。

**建議修法**：將陣列大小改為 6：
```c
robj *argv[6];
```

**判斷依據**：diff 中新增的程式碼片段：
```c
+        robj *argv[5];
+        argv[0] = shared.hpexpireat;
+        argv[1] = c->argv[1];
+        argv[2] = createStringObjectFromLongLong(expireat);
+        argv[3] = shared.fields;
+        argv[4] = shared.integers[1];
+        argv[5] = c->argv[2];
```
陣列大小為 5，但使用了索引 5，總共 6 個元素。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2309</code> 手動傳播 HPEXPIREAT 時 expireat 的型別轉換可能導致溢位</summary>

`expireat` 是 `uint64_t`，但 `createStringObjectFromLongLong` 接受 `long long`（有號 64 位元）。如果 `expireat` 的值大於 `LLONG_MAX`，轉換為 `long long` 會產生實作定義的行為（通常是負數），導致傳播錯誤的過期時間。

**失敗情境**：當過期時間設定為超過 `LLONG_MAX` 毫秒（約西元 292471 年）時，轉換後可能變成負數，傳播到複本後會立即過期或產生非預期行為。

**建議修法**：使用 `createStringObjectFromLongLong` 前先檢查 `expireat` 是否在 `long long` 範圍內，或改用其他能處理 `uint64_t` 的函式（如 `createStringObjectFromLongLong` 的無號版本，或自行轉換為字串）。

**判斷依據**：diff 中新增的程式碼片段：
```c
+        argv[2] = createStringObjectFromLongLong(expireat);
```
`expireat` 的型別是 `uint64_t`，而 `createStringObjectFromLongLong` 的參數型別是 `long long`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/t_hash.c:2313</code> 手動傳播 HPEXPIREAT 時未檢查 alsoPropagate 的返回值</summary>

`alsoPropagate` 可能因為記憶體不足等原因失敗，但程式碼未檢查其返回值。雖然在 Redis 中通常會直接 panic，但此處未遵循該慣例，可能導致錯誤被忽略。

**失敗情境**：在記憶體極度不足時，`alsoPropagate` 可能無法成功傳播命令，但程式繼續執行，導致複本資料不一致。

**建議修法**：檢查 `alsoPropagate` 的返回值，若失敗則進行適當處理（如 `serverPanic`）。

**判斷依據**：diff 中新增的程式碼片段：
```c
+        alsoPropagate(c->db->id, argv, 6, PROPAGATE_AOF|PROPAGATE_REPL);
```
未檢查返回值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1314</code> 測試未驗證複本上 HINCRBYFLOAT 的實際值</summary>

測試中在複本上執行 `r -1 hincrbyfloat h1 f1 1.1` 後，只檢查了 TTL 範圍和與主節點的值相等，但未直接驗證複本上的值是否正確（例如應為 2.1）。雖然與主節點比較可以間接驗證，但若主節點也有 bug，測試可能無法發現。

**失敗情境**：如果主節點和複本都錯誤地將值設為 1.1，測試仍會通過，因為兩者相等。

**建議修法**：增加對複本值的直接斷言，例如 `assert_equal {2.1} [r hget h1 f1]`。

**判斷依據**：diff 中新增的測試程式碼：
```tcl
+                assert_equal [r -1 hget h1 f1] [r hget h1 f1]
```
僅比較主從值，未直接驗證值。

</details>

<details><summary>🔹 <b>Nit</b> — <code>src/t_hash.c:2244</code> 變數命名 unused_flag 可能造成混淆</summary>

在 `hincrbyfloatCommand` 中新增了 `int unused_flag = 0;`，但此變數似乎未被使用。這可能是開發過程中的殘留，建議移除。

**失敗情境**：無直接功能影響，但可能誤導讀者。

**建議修法**：刪除未使用的變數。

**判斷依據**：diff 中新增的程式碼片段：
```c
+    int unused_flag = 0;
```
後續程式碼未使用此變數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4972 (cache hit 4864) ｜ completion tokens 2426 ｜ PR #8</sub>