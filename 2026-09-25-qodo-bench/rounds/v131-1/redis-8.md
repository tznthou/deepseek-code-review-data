<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在 replica 上會移除欄位過期時間的問題。主要變更為讓 hashTypeGetValue 可回傳過期時間，並在 hincrbyfloatCommand 中，若欄位有過期時間，則以 HSET + HPEXPIREAT 的方式傳播。整體方向正確，但發現一個可能導致記憶體洩漏的問題：在傳播 HPEXPIREAT 時，argv[2] 建立的 robj 未釋放。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2309` | 記憶體洩漏：argv[2] 建立的 robj 未釋放 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2309</code> 記憶體洩漏：argv[2] 建立的 robj 未釋放</summary>

在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後未呼叫 decrRefCount 釋放。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。建議在 alsoPropagate 呼叫後立即釋放 argv[2]，或改用其他方式避免手動管理記憶體。

**判斷依據**：diff 中新增的程式碼：
+        argv[2] = createStringObjectFromLongLong(expireat);
+        argv[3] = shared.fields;
+        argv[4] = shared.integers[1];
+        argv[5] = c->argv[2];
+        alsoPropagate(c->db->id, argv, 6, PROPAGATE_AOF|PROPAGATE_REPL);

在 alsoPropagate 之後沒有對 argv[2] 呼叫 decrRefCount。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4972 (cache hit 1408) ｜ completion tokens 467 ｜ PR #8</sub>