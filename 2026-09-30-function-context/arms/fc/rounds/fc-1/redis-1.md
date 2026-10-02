<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式進行轉換。整體方向合理，可避免狀態切換的脆弱性，但實作上存在多個正確性與相容性風險：dictGetHash 不再處理 stored key、dictSetKeyAtLink 在 newItem=0 時使用 addedKey 而非原始 key 進行查找、validateStoredKeyConversion 未使用、hashTypeDelete 的簽章變更可能破壞外部模組 ABI、以及 memory_prefetch.c 中 dictCompareKeys 的呼叫可能傳入錯誤型別。建議先修正上述問題再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/dict.c:1808` | dictGetHash 不再處理 stored key，可能導致雜湊不一致 | 0.95 |
| ⚠️ | Major | `src/dict.c:913` | dictSetKeyAtLink 在 newItem=0 時使用 addedKey 查找，可能找不到既有鍵 | 0.85 |
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 未使用，可能導致錯誤的 keyFromStoredKey 未被偵測 | 0.80 |
| ⚠️ | Major | `src/server.h:3658` | hashTypeDelete 簽章變更可能破壞外部模組 ABI | 0.80 |
| ⚠️ | Major | `src/memory_prefetch.c:233` | dictCompareKeys 呼叫可能傳入錯誤型別 | 0.75 |
| 🔸 | Minor | `src/dict.c:533` | dictAddRaw 中 keyDup 的型別標記可能不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/dict.c:1808</code> dictGetHash 不再處理 stored key，可能導致雜湊不一致</summary>

`dictGetHash` 現在直接呼叫 `d->type->hashFunction(key)`，但 `key` 可能是 stored key（例如 kvobj 指標），而 `hashFunction` 預期的是 lookup key（例如 sds）。在 `rehashEntriesInBucketAtIndex` 中，程式碼先取得 storedKey，再呼叫 `dictStoredKey2Key` 轉換後才呼叫 `dictGetHash`，但其他呼叫點（如 `dictFindLinkInternal`、`dictGenericDelete`、`dictTwoPhaseUnlinkFind`、`dictFindLinkForInsert`）傳入的 `key` 參數可能是 stored key 或 lookup key，取決於呼叫者。若呼叫者傳入 stored key，則 `dictGetHash` 會以錯誤的型別計算雜湊，導致查找失敗或雜湊表損毀。

**失敗情境**：當 `dbDictType` 的 `keyFromStoredKey` 設為 `kvGetKey` 時，若程式碼呼叫 `dictFind(d, kvobj)` 而非先轉換成 sds，則 `dictGetHash` 會將 kvobj 指標當作 sds 來計算長度，可能讀取無效記憶體或產生錯誤雜湊。

**建議**：在 `dictGetHash` 內部先呼叫 `dictStoredKey2Key` 轉換，或明確規定所有公開 API 的 `key` 參數必須是 lookup key，並在內部轉換 stored key。

**判斷依據**：diff 中 `dictGetHash` 的實作從 `dictHashKey(d, key, d->useStoredKeyApi)` 改為 `d->type->hashFunction(key)`，但 `dictHashKey` 原本會根據 `isStoredKey` 選擇 `storedHashFunction` 或 `hashFunction`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:913</code> dictSetKeyAtLink 在 newItem=0 時使用 addedKey 查找，可能找不到既有鍵</summary>

在 `dictSetKeyAtLink` 的 `newItem == 0` 分支中，原本使用 `key` 呼叫 `dictFindLink`，現在改為使用 `addedKey`。但 `addedKey` 是經過 `keyDup` 複製後的新指標，若 `keyDup` 有實作（例如某些 dict type），則 `addedKey` 與原本儲存在 dict 中的 key 指標不同，導致 `dictFindLink` 無法找到對應的 entry，進而觸發 assert 失敗或錯誤更新。

**失敗情境**：若 dict type 有 `keyDup` 回呼，且呼叫 `dictSetKeyAtLink(d, newKey, &link, 0)` 來更新既有 entry 的 key，則 `addedKey` 是新複製的 key，與 dict 中儲存的舊 key 不同，`dictFindLink` 會找不到，導致 assert 失敗。

**建議**：應使用原始的 `key` 進行查找，而不是 `addedKey`。

**判斷依據**：diff 中 `dictSetKeyAtLink` 的 `newItem == 0` 分支從 `dictFindLink(d, key, NULL)` 改為 `dictFindLink(d, addedKey, NULL)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 未使用，可能導致錯誤的 keyFromStoredKey 未被偵測</summary>

新增的 `validateStoredKeyConversion` 函式從未被呼叫。若 dict type 的 `keyFromStoredKey` 回呼有誤（例如回傳 NULL 或錯誤指標），將導致後續雜湊或比較作業出錯，且難以除錯。

**建議**：在 dict 初始化或首次使用時呼叫此驗證函式，或移除該函式以避免 dead code。

**判斷依據**：diff 中新增此函式，但搜尋整個 diff 未見任何呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.h:3658</code> hashTypeDelete 簽章變更可能破壞外部模組 ABI</summary>

`hashTypeDelete` 的簽章從 `int hashTypeDelete(robj *o, void *key, int isSdsField)` 改為 `int hashTypeDelete(robj *o, void *key)`。此函式可能被外部 Redis 模組使用（雖然未在公開 API 中列出，但可能被內部或第三方模組直接呼叫）。移除參數會導致 ABI 不相容，若外部模組仍以舊簽章呼叫，將導致堆疊損毀或錯誤行為。

**建議**：若此函式非公開 API，可忽略；否則應保留舊簽章並提供新函式，或增加版本檢查。

**判斷依據**：diff 中 `server.h` 的宣告從 `int hashTypeDelete(robj *o, void *key, int isSdsField);` 改為 `int hashTypeDelete(robj *o, void *key);`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/memory_prefetch.c:233</code> dictCompareKeys 呼叫可能傳入錯誤型別</summary>

在 `prefetchValueData` 中，新增了 `sds key = kvobjGetKey(kv);`，然後呼叫 `dictCompareKeys(batch->current_dicts[i], batch->keys[i], key)`。但 `batch->keys[i]` 的型別未知，可能是 stored key（kvobj）或 lookup key（sds）。若 `batch->keys[i]` 是 stored key，而 `key` 是 sds，則 `dictCompareKeys` 內部會將兩者視為相同型別進行比較，可能導致錯誤結果。

**失敗情境**：若 `batch->keys[i]` 是 kvobj 指標，則 `dictCompareKeys` 會將 kvobj 與 sds 進行比較，可能誤判為不相等，導致 prefetch 錯過正確 entry。

**建議**：確認 `batch->keys[i]` 的型別，並在呼叫前進行適當轉換。

**判斷依據**：diff 中新增 `sds key = kvobjGetKey(kv);` 並傳入 `dictCompareKeys`，但未確認 `batch->keys[i]` 的型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:533</code> dictAddRaw 中 keyDup 的型別標記可能不一致</summary>

`dictAddRaw` 的參數 `key` 被標記為 `__stored_key`，但在呼叫 `dictFindLinkForInsert` 前先轉換成 lookup key，然後在 `keyDup` 時又直接使用原始的 `key`。若 `keyDup` 預期 stored key，則此處正確；但若 `keyDup` 預期 lookup key，則可能出錯。需要確認所有 dict type 的 `keyDup` 實作。

**建議**：檢查所有 `keyDup` 回呼，確保它們能處理 stored key。

**判斷依據**：diff 中 `dictAddRaw` 的 `key` 參數標記為 `__stored_key`，但 `keyDup` 的呼叫未經轉換。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 38444 (cache hit 1536) ｜ completion tokens 2415 ｜ PR #1</sub>