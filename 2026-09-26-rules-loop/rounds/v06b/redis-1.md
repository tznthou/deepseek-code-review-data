<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域開關（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，並移除了 storedHashFunction 與 storedKeyCompare。整體設計更簡潔，但存在一些正確性與相容性風險：validateStoredKeyConversion 函式未被使用，且其邏輯可能錯誤；dictSetKeyAtLink 中新增的 keyDup 呼叫可能導致記憶體洩漏或重複釋放；hashTypeDelete 的簽名變更可能遺漏呼叫點。建議先修正這些問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未被使用且邏輯可能錯誤 | 0.80 |
| ⚠️ | Major | `src/dict.c:890` | dictSetKeyAtLink 中新增的 keyDup 呼叫可能導致記憶體洩漏或重複釋放 | 0.75 |
| ⚠️ | Major | `src/server.h:3658` | hashTypeDelete 簽名變更可能遺漏呼叫點 | 0.70 |
| 🔸 | Minor | `src/dict.c:336` | rehashEntriesInBucketAtIndex 中可能遺漏 keyFromStoredKey 轉換 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未被使用且邏輯可能錯誤</summary>

新增的 validateStoredKeyConversion 函式在整個 diff 中沒有被呼叫，這可能是未完成的重構。此外，其邏輯：當 keyFromStoredKey 存在時，僅檢查 extracted != NULL，但 keyFromStoredKey 可能合法地回傳 NULL（例如鍵值為 NULL 的 dict），這會導致誤判。建議移除該函式或修正其邏輯並在適當位置呼叫。

**判斷依據**：diff 中新增了 validateStoredKeyConversion 函式，但搜尋整個 diff 未見任何呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:890</code> dictSetKeyAtLink 中新增的 keyDup 呼叫可能導致記憶體洩漏或重複釋放</summary>

在 dictSetKeyAtLink 中，原本直接使用 key，現在改為先呼叫 keyDup 得到 addedKey，然後在後續使用 addedKey。但若 keyDup 回傳新配置的記憶體，而後續流程中又對該記憶體進行釋放（例如在錯誤路徑或替換時），可能造成雙重釋放或洩漏。需要檢查所有呼叫 dictSetKeyAtLink 的地方，確認 key 的生命週期管理是否一致。

**判斷依據**：diff 中新增了 keyDup 呼叫，但未見對應的釋放邏輯調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.h:3658</code> hashTypeDelete 簽名變更可能遺漏呼叫點</summary>

hashTypeDelete 的簽名從 (robj *o, void *key, int isSdsField) 改為 (robj *o, void *key)，移除了 isSdsField 參數。但 diff 中只更新了部分呼叫點，可能還有其他檔案中的呼叫未更新，導致編譯錯誤或行為錯誤。建議全域搜尋 hashTypeDelete 的所有呼叫並確認。

**判斷依據**：diff 中修改了多處 hashTypeDelete 呼叫，但無法確認是否涵蓋所有呼叫點。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:336</code> rehashEntriesInBucketAtIndex 中可能遺漏 keyFromStoredKey 轉換</summary>

在 rehashEntriesInBucketAtIndex 中，當縮表時（else 分支），直接使用 storedKey 進行後續處理，但未呼叫 dictStoredKey2Key 轉換。若 keyFromStoredKey 存在且 storedKey 與 key 不同，可能導致後續比較或雜湊錯誤。建議檢查該分支是否需要轉換。

**判斷依據**：diff 中僅在擴表分支呼叫了 dictStoredKey2Key，縮表分支未呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12902 (cache hit 12800) ｜ completion tokens 1162 ｜ PR #1</sub>