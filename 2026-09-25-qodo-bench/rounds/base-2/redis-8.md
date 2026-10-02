<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題。主要變更在 hashTypeGetValue 增加 expiredAt 輸出參數，並在 hincrbyfloatCommand 中手動傳播 HSET 與 HPEXPIREAT 命令。整體方向正確，但存在一個嚴重的記憶體洩漏（argv[2] 未釋放），以及一個邊界條件變更（>= 改為 >）可能造成行為差異，需要進一步確認。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2309` | 記憶體洩漏：argv[2] 未釋放 | 0.95 |
| ⚠️ | Major | `src/t_hash.c:742` | 邊界條件變更：>= 改為 > 可能影響過期判斷 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2309</code> 記憶體洩漏：argv[2] 未釋放</summary>

在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);`，但在 `alsoPropagate` 之後沒有呼叫 `decrRefCount(argv[2])`。這會導致每次執行此路徑時洩漏一個 string object 的記憶體。建議在 `alsoPropagate` 之後加入 `decrRefCount(argv[2]);`。

**判斷依據**：diff 中新增的程式碼片段顯示 `argv[2]` 被建立後沒有對應的 `decrRefCount`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:742</code> 邊界條件變更：>= 改為 > 可能影響過期判斷</summary>

原本的判斷是 `if (expiredAt >= (uint64_t) commandTimeSnapshot())`，現在改為 `if (*expiredAt > (uint64_t) commandTimeSnapshot())`。這表示當 `expiredAt` 等於當前時間時，原本會被視為未過期，現在會被視為已過期。這可能導致在時間邊界上的行為差異，例如欄位剛好在同一毫秒過期時，原本可能回傳值，現在會回傳過期。需要確認此變更是否為預期行為，並考慮是否應保留 `>=` 以維持原有語意。

**判斷依據**：diff 中此行由 `>=` 改為 `>`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5008 (cache hit 4992) ｜ completion tokens 717 ｜ PR #8</sub>