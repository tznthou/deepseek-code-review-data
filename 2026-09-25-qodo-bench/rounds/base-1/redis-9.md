<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正 HINCRBYFLOAT 在複本上移除欄位過期時間的問題，方法是將複寫指令從 HSET 改為 HSETEX KEEPTTL FIELDS 1。主要風險在於新增的 shared 物件（hsetex、fields）未在 server.h 中正確宣告，可能導致編譯錯誤；此外測試中對 f2 的 TTL 斷言與註解不一致，需確認預期行為。整體邏輯合理，但需先解決編譯問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/server.h:1529` | shared 物件宣告順序不一致可能導致編譯錯誤 | 0.95 |
| ⚠️ | Major | `tests/unit/type/hash-field-expire.tcl:1996` | 測試中對 f2 的 TTL 斷言與註解不一致 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>src/server.h:1529</code> shared 物件宣告順序不一致可能導致編譯錯誤</summary>

在 `server.h` 的 `sharedObjectsStruct` 中，新增的 `hsetex` 和 `fields` 被插入在既有成員之間，但 `server.c` 中 `createSharedObjects()` 的初始化順序與宣告順序不一致。這會導致 `shared.hsetex` 和 `shared.fields` 在執行時指向錯誤的物件（例如 `shared.hsetex` 可能指向 `shared.hpersist`），造成未定義行為或執行期錯誤。

建議將 `server.h` 中的宣告順序調整為與 `server.c` 中的初始化順序完全一致，或將新增成員放在結構體末端以避免此類問題。

**判斷依據**：diff 中 `server.h` 的修改顯示 `hsetex` 被加在 `hpersist` 之後，而 `fields` 被加在 `createconsumer` 之後；但 `server.c` 中 `hsetex` 的初始化在 `hdel` 之後，`fields` 的初始化在 `redacted` 之後，順序不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/unit/type/hash-field-expire.tcl:1996</code> 測試中對 f2 的 TTL 斷言與註解不一致</summary>

測試中對 f2 的 TTL 斷言為 `assert_equal {-1} [r httl h1 FIELDS 1 f2]`，但註解寫著「The field f2 should not have any expiration on replica either even though it was set using HSET with KEEPTTL flag.」這可能造成混淆：f2 原本就沒有 TTL，因此預期為 -1 是合理的，但註解暗示它被 HSETEX KEEPTTL 設定過。建議釐清註解或斷言，確保測試意圖明確。

**判斷依據**：diff 中新增的測試區塊包含此行，且上方註解提到 f2 被 HSETEX KEEPTTL 設定，但實際 f2 是透過 HSET 設定且無 TTL。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3603 (cache hit 1536) ｜ completion tokens 823 ｜ PR #9</sub>