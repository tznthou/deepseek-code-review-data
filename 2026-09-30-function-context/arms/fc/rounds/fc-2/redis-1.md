<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式進行轉換。整體方向合理，可消除全域狀態並簡化呼叫端。主要風險在於轉換邏輯的正確性，特別是 dictStoredKey2Key 的實作、hashTypeDelete 的參數移除，以及記憶體預取路徑的變更。建議先修正 dictStoredKey2Key 的型別問題，並確認 hashTypeDelete 的所有呼叫點都傳入正確的 key 型別。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:97` | dictStoredKey2Key 回傳型別可能導致未定義行為 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:1257` | hashTypeDelete 移除 isSdsField 參數後，呼叫端可能傳入錯誤型別 | 0.75 |
| 🔸 | Minor | `src/memory_prefetch.c:233` | prefetchValueData 中新增的 key 變數可能造成不必要的複製 | 0.60 |
| 🔸 | Minor | `src/dict.h:66` | __stored_key 巨集定義為空，可能失去型別安全 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:97</code> dictStoredKey2Key 回傳型別可能導致未定義行為</summary>

`dictStoredKey2Key` 宣告為回傳 `const void *`，但 `keyFromStoredKey` 回呼的簽章是 `const void *(*keyFromStoredKey)(const void *key __stored_key)`。若回呼回傳的指標並非指向有效物件（例如回傳 NULL 或錯誤指標），呼叫端可能解參考無效指標。此外，`validateStoredKeyConversion` 僅檢查非 NULL，未驗證指標有效性。建議明確規範回呼不得回傳 NULL，並在必要處加入斷言。

**判斷依據**：diff 中新增的 dictStoredKey2Key 函式，以及 dictType 中 keyFromStoredKey 的宣告。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:1257</code> hashTypeDelete 移除 isSdsField 參數後，呼叫端可能傳入錯誤型別</summary>

`hashTypeDelete` 原本接受 `isSdsField` 參數來區分 field 是 sds 或 Entry*。移除後，函式內部直接假設 field 是 sds（呼叫 `sdslen`）。但檢查所有呼叫點後發現，`onFieldExpire` 傳入的是 `entryGetField(e)`（sds），而其他呼叫點傳入的也是 sds，因此目前可能安全。然而，若未來有呼叫點傳入 Entry*，將導致 `sdslen` 對非 sds 指標操作，造成未定義行為。建議在函式開頭加入斷言或型別檢查，或保留參數以明確意圖。

**判斷依據**：diff 中 hashTypeDelete 的簽章變更，以及所有呼叫點的修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/memory_prefetch.c:233</code> prefetchValueData 中新增的 key 變數可能造成不必要的複製</summary>

在 `prefetchValueData` 中新增 `sds key = kvobjGetKey(kv);`，但此 key 僅用於 `dictCompareKeys` 的第三個參數。若 `kvobjGetKey` 回傳的 sds 需要複製，可能增加效能負擔。建議確認 `kvobjGetKey` 是否僅回傳指標，或考慮直接傳遞 `kv` 並在比較函式中提取 key。

**判斷依據**：diff 中新增的這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:66</code> __stored_key 巨集定義為空，可能失去型別安全</summary>

`__stored_key` 被定義為空巨集，僅作為註解用途。這無法在編譯時期強制區分 stored key 與 lookup key，可能導致誤用。建議使用更明確的型別或屬性（例如 `__attribute__((address_space(1)))`）來增加型別安全，或至少在文件上強調其僅為標記。

**判斷依據**：diff 中新增的巨集定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 38444 (cache hit 38400) ｜ completion tokens 1142 ｜ PR #1</sub>