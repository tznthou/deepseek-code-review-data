<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，並移除了 storedHashFunction/storedKeyCompare。整體方向合理，可消除脆弱的狀態切換。但存在幾個關鍵問題：validateStoredKeyConversion 函式未使用，且其邏輯可能導致誤判；dictSetKeyAtLink 中新增的 dictFindLink 呼叫可能造成效能回歸；hashTypeDelete 的簽名變更後，呼叫端傳入的 key 類型不一致，可能導致記憶體錯誤。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/t_hash.c:3503` | hashTypeDelete 簽名變更後，呼叫端傳入的 key 類型不一致 | 0.95 |
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未使用且邏輯有誤 | 0.90 |
| ⚠️ | Major | `src/dict.c:913` | dictSetKeyAtLink 中新增 dictFindLink 呼叫可能造成效能回歸 | 0.85 |
| 🔸 | Minor | `src/dict.c:102` | validateStoredKeyConversion 可能違反 R04（未使用函式警告） | 0.70 |
| 🔸 | Minor | `src/dict.h:157` | pauseAutoResize 型別變更可能影響 ABI 相容性 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/t_hash.c:3503</code> hashTypeDelete 簽名變更後，呼叫端傳入的 key 類型不一致</summary>

hashTypeDelete 原本接受 isSdsField 參數來區分 key 是 sds 還是 entry*，現在移除該參數，假設所有呼叫都傳入 sds。然而，在 onFieldExpire 中，原本呼叫 hashTypeDelete(expCtx->hashObj, field, 0)，其中 field 是 entry*（非 sds），現在改為 hashTypeDelete(expCtx->hashObj, field)，但函式內部會執行 sdslen((sds)field)，這將導致對 entry* 指標進行 sdslen 操作，可能造成記憶體錯誤或崩潰。需要修正 onFieldExpire 中的呼叫，或調整 hashTypeDelete 的實作以正確處理不同類型的 key。

**判斷依據**：diff 中 onFieldExpire 的呼叫從 hashTypeDelete(expCtx->hashObj, field, 0) 改為 hashTypeDelete(expCtx->hashObj, field)，但 hashTypeDelete 內部仍使用 sdslen((sds)field)。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未使用且邏輯有誤</summary>

新增的 validateStoredKeyConversion 函式從未被呼叫，且其邏輯有問題：當 keyFromStoredKey 存在時，它只檢查回傳值是否為 NULL，但 keyFromStoredKey 可能合法回傳 NULL（例如空字串？），且未驗證回傳的 key 是否與原始 stored key 一致。此外，該函式可能被編譯器警告為未使用（違反 R04）。建議移除該函式，或若需驗證，應在初始化時呼叫並修正邏輯。

**判斷依據**：diff 中新增了 validateStoredKeyConversion 函式，但未見任何呼叫。且其回傳值僅用於檢查，未實際使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:913</code> dictSetKeyAtLink 中新增 dictFindLink 呼叫可能造成效能回歸</summary>

在 dictSetKeyAtLink 中，當 *link 為 NULL 時，原本直接使用傳入的 key 進行查找，現在改為先呼叫 dictStoredKey2Key 取得 addedKey，再呼叫 dictFindLink(d, addedKey, NULL)。這會導致額外的 hash 計算和比較，且可能破壞原本的效能假設。此外，若 keyFromStoredKey 回傳的 key 與原始 key 不同，可能導致查找失敗。建議確認此變更的必要性，或改為直接使用原始 key 進行查找。

**判斷依據**：diff 中將原本的 dictFindLink(d, key, NULL) 改為 dictFindLink(d, addedKey, NULL)，其中 addedKey 是經過 keyDup 或直接賦值的 key。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 可能違反 R04（未使用函式警告）</summary>

validateStoredKeyConversion 函式未被使用，若編譯器開啟 -Wunused-function 且 -Werror，將導致編譯失敗。建議移除或標記為 unused。

**判斷依據**：函式定義後未見任何呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:157</code> pauseAutoResize 型別變更可能影響 ABI 相容性</summary>

pauseAutoResize 從 bitfield 改為 int16_t，可能改變 struct dict 的佈局，影響與外部模組的 ABI 相容性。若 Redis 作為動態庫提供，可能導致崩潰。建議確認此變更的必要性，或保持原有 bitfield 佈局。

**判斷依據**：diff 中將 signed pauseAutoResize: 15; 改為 int16_t pauseAutoResize;

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12922 (cache hit 11904) ｜ completion tokens 1467 ｜ PR #1</sub>