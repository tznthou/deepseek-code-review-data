<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題。主要變更包括：在 hashTypeGetValue 增加 expiredAt 輸出參數、在 hincrbyfloatCommand 中偵測欄位是否有過期時間，並在需要時以 HSET + HPEXPIREAT 的 MULTI/EXEC 形式傳播。整體方向正確，但存在一個明確的陣列越界錯誤（argv 宣告大小為 5 但寫入 6 個元素），可能導致記憶體損壞或當機，必須修正。此外，測試中對複製流的斷言可能因 MULTI/EXEC 包裹方式而失敗，需要確認。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2306` | argv 陣列宣告大小為 5，但寫入 6 個元素，導致堆疊緩衝區溢位 | 0.99 |
| ⚠️ | Major | `tests/unit/type/hash-field-expire.tcl:1190` | 測試中對複製流的斷言可能因 MULTI/EXEC 包裹方式而失敗 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2306</code> argv 陣列宣告大小為 5，但寫入 6 個元素，導致堆疊緩衝區溢位</summary>

在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼宣告 `robj *argv[5];`，但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成堆疊緩衝區溢位。這可能導致記憶體損壞、程式當機，甚至可能被利用。

建議修正：將陣列大小改為 6，例如 `robj *argv[6];`。

**判斷依據**：diff 中新增的程式碼片段：
```
+        robj *argv[5];
+        argv[0] = shared.hpexpireat;
+        argv[1] = c->argv[1];
+        argv[2] = createStringObjectFromLongLong(expireat);
+        argv[3] = shared.fields;
+        argv[4] = shared.integers[1];
+        argv[5] = c->argv[2];
```
陣列大小為 5，但索引 0 到 5 共 6 個元素，超出範圍。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/type/hash-field-expire.tcl:1190</code> 測試中對複製流的斷言可能因 MULTI/EXEC 包裹方式而失敗</summary>

在測試 `HINCRBYFLOAT command won't remove field expiration on replica` 中，`assert_replication_stream` 期望的序列包含 `{multi}`、`{hset h1 f1 *}`、`{hpexpireat h1 * FIELDS 1 f1}`、`{exec}`。然而，實際傳播的 MULTI/EXEC 可能不會以這種方式呈現，或者可能因為 `alsoPropagate` 的呼叫方式而導致順序或包裹方式不同。建議確認實際複製流的格式，或調整斷言以符合實際行為。

**判斷依據**：diff 中新增的測試斷言片段。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13233 (cache hit 13184) ｜ completion tokens 992 ｜ PR #8</sub>