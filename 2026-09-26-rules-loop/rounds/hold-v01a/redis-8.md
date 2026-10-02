<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位過期時間的問題。主要變更包括：hashTypeGetValue 新增 expiredAt 輸出參數、hincrbyfloatCommand 在欄位有過期時間時手動傳播 HSET 與 HPEXPIREAT 指令，並新增對應的複製測試。整體方向正確，但存在一個嚴重的記憶體洩漏（argv[2] 未釋放），以及一個可能導致測試不穩定的 TTL 範圍過窄問題。建議先修正記憶體洩漏再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:2309` | 記憶體洩漏：argv[2] 使用 createStringObjectFromLongLong 建立後未釋放 | 0.95 |
| ⚠️ | Major | `tests/unit/type/hash-field-expire.tcl:1300` | 測試中 TTL 範圍過窄可能導致不穩定 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:2309</code> 記憶體洩漏：argv[2] 使用 createStringObjectFromLongLong 建立後未釋放</summary>

在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後沒有對其呼叫 decrRefCount。這會導致每次執行此路徑時洩漏一個 robj。

失敗情境：任何對具有過期時間的 hash 欄位執行 HINCRBYFLOAT 的請求，都會造成記憶體洩漏，長期下來可能耗盡記憶體。

建議修法：在 alsoPropagate 呼叫之後，加入 decrRefCount(argv[2]); 釋放該物件。

**判斷依據**：diff 中新增的這一行建立了 robj，但後續沒有對應的 decrRefCount 呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/type/hash-field-expire.tcl:1300</code> 測試中 TTL 範圍過窄可能導致不穩定</summary>

測試使用 assert_range [r httl h1 FIELDS 1 f1] 90 100 來驗證 TTL。但 TTL 會隨時間遞減，若測試執行較慢（例如在 CI 負載高時），TTL 可能低於 90，導致測試失敗。

失敗情境：在慢速環境下，從設定過期到檢查 TTL 之間經過超過 10 秒，TTL 將低於 90，assert_range 失敗。

建議修法：放寬範圍，例如改為 assert_range [r httl h1 FIELDS 1 f1] 80 100，或使用更精確的等待機制。

**判斷依據**：diff 中新增的測試行，TTL 下限 90 過於嚴格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6009 (cache hit 4992) ｜ completion tokens 724 ｜ PR #8</sub>