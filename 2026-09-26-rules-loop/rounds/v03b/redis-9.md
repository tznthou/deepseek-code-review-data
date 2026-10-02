<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在 replica 上會移除 field expiration 的問題，方法是將複寫指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標。主要風險在於新增的 shared objects（hsetex、fields）是否正確初始化，以及複寫指令的參數順序是否與命令定義一致。測試涵蓋了 replica 同步情境，但需確認測試中使用的 PXAT 與 KEEPTTL 組合是否為合法用法。整體而言，變更範圍小且目標明確，但需驗證命令格式的正確性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2571` | 複寫指令 HSETEX 的參數順序可能與命令定義不符 | 0.75 |
| 🔸 | Minor | `src/server.c:2130` | 新增 shared object 未確認是否在所有初始化路徑中建立 | 0.60 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1972` | 測試中 HSETEX 使用 PXAT 與 KEEPTTL 的組合可能不合法 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2571</code> 複寫指令 HSETEX 的參數順序可能與命令定義不符</summary>

在 `rewriteClientCommandVector` 中，參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。需要確認 HSETEX 命令的語法是否為 `HSETEX key [KEEPTTL] FIELDS numfields field value [field value ...]`。若 KEEPTTL 的位置或 FIELDS 的用法有誤，可能導致 replica 執行失敗或行為錯誤。建議查閱命令定義或測試驗證。

**判斷依據**：diff 中新增的 rewriteClientCommandVector 呼叫，參數順序與常見 HSETEX 語法可能不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.c:2130</code> 新增 shared object 未確認是否在所有初始化路徑中建立</summary>

新增了 `shared.hsetex` 和 `shared.fields`，但需確認 `createSharedObjects` 是否在所有啟動路徑（如 Sentinel、module）中被呼叫，且沒有遺漏。若某些路徑未初始化這些 shared objects，可能導致 null pointer dereference。

**判斷依據**：diff 中新增的 shared object 建立，但未見其他初始化路徑的修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1972</code> 測試中 HSETEX 使用 PXAT 與 KEEPTTL 的組合可能不合法</summary>

測試中預期複寫指令為 `hsetex h1 PXAT * FIELDS 1 f1 1`，但 PXAT 與 KEEPTTL 是否可同時使用需確認。若命令不允許此組合，測試將失敗或無法驗證預期行為。

**判斷依據**：diff 中測試預期的複寫指令包含 PXAT 與 KEEPTTL，但未見命令定義支持此組合。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4614 (cache hit 4608) ｜ completion tokens 844 ｜ PR #9</sub>