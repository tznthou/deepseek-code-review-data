<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，以消除易錯的全域狀態管理。整體設計合理，但存在一些正確性與相容性疑慮，特別是在 hashTypeDelete 的參數移除、dictSetKeyAtLink 的 keyDup 使用，以及 validateStoredKeyConversion 的未使用。建議修正後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未使用 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:1257` | hashTypeDelete 移除 isSdsField 參數可能導致錯誤的 dictDelete 呼叫 | 0.75 |
| ⚠️ | Major | `src/dict.c:890` | dictSetKeyAtLink 中 keyDup 可能重複複製 stored-key | 0.70 |
| 🔸 | Minor | `src/dict.c:339` | rehashEntriesInBucketAtIndex 中 storedKey 可能為 NULL | 0.60 |
| 🔸 | Minor | `src/dict.h:157` | pauseAutoResize 型別從 bitfield 改為 int16_t 可能影響 ABI | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未使用</summary>

新增的 validateStoredKeyConversion 函式在整個 diff 中沒有被呼叫。這可能是為了驗證 keyFromStoredKey 回呼的正確性，但若未使用，則無法提供任何保障，且可能觸發編譯器警告（-Wunused-function），違反 R04。建議移除該函式，或實際在 dict 初始化或插入時呼叫它。

**判斷依據**：diff 中新增了 validateStoredKeyConversion 函式，但後續沒有呼叫它的程式碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:1257</code> hashTypeDelete 移除 isSdsField 參數可能導致錯誤的 dictDelete 呼叫</summary>

原本 hashTypeDelete 接受 isSdsField 參數來決定是否使用 stored-key API。移除後，函式內直接呼叫 dictDelete，但 dictDelete 現在預期 key 為 lookup key（sds），而呼叫者可能傳入 Entry*（stored-key）。在 onFieldExpire 中，原本傳入 isSdsField=0，表示 field 是 Entry*，但現在直接傳入 field，可能導致 dictDelete 將 Entry* 當作 sds 處理，造成記憶體錯誤或找不到鍵。建議保留參數或明確區分呼叫者傳入的型別。

**判斷依據**：diff 中 hashTypeDelete 的簽名從 (robj *o, void *key, int isSdsField) 改為 (robj *o, void *key)，且呼叫點 onFieldExpire 原本傳入 isSdsField=0，現在直接傳入 field。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:890</code> dictSetKeyAtLink 中 keyDup 可能重複複製 stored-key</summary>

在 dictSetKeyAtLink 中，addedKey 是透過 keyDup 複製 key 得到的。但 key 現在是 stored-key，而 keyDup 的簽名已改為接受 stored-key。若 keyDup 實作會從 stored-key 提取 lookup key 再複製，則可能導致重複複製或型別不符。需要確認所有 keyDup 實作是否正確處理 stored-key。

**判斷依據**：diff 中 dictSetKeyAtLink 的 key 參數標記為 __stored_key，且 keyDup 的簽名也改為接受 __stored_key，但未檢查 keyDup 實作是否正確。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:339</code> rehashEntriesInBucketAtIndex 中 storedKey 可能為 NULL</summary>

在 rehashEntriesInBucketAtIndex 中，storedKey 從 dictGetKey(de) 取得，但若 de 是 key-only entry（entryIsKey(de) 為真），則 storedKey 可能不是有效的指標。後續呼叫 dictStoredKey2Key(d, storedKey) 可能導致 NULL 解參考。需要確認 entryIsKey 的情況。

**判斷依據**：diff 中新增了 storedKey 變數，但未檢查 entryIsKey(de) 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:157</code> pauseAutoResize 型別從 bitfield 改為 int16_t 可能影響 ABI</summary>

原本 pauseAutoResize 是 15-bit signed bitfield，現在改為 int16_t。這可能改變 struct dict 的佈局，影響與外部模組的 ABI 相容性。若 Redis 作為動態連結庫使用，可能導致問題。建議確認 ABI 穩定性要求。

**判斷依據**：diff 中 struct dict 的 pauseAutoResize 欄位型別從 bitfield 改為 int16_t。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12902 (cache hit 11904) ｜ completion tokens 1387 ｜ PR #1</sub>