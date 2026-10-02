<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域開關（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式來轉換 stored-key 與 lookup key。整體方向合理，可消除狀態切換的脆弱性，但改動範圍大且涉及核心資料結構，需特別注意正確性與相容性。主要風險在於 hashTypeDelete 的介面簡化可能遺漏某些呼叫點、dictSetKeyAtLink 中新增的 validateStoredKeyConversion 未被使用、以及 keyFromStoredKey 回呼的錯誤處理不足。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/dict.c:102` | validateStoredKeyConversion 函式未被使用 | 0.80 |
| ⚠️ | Major | `src/t_hash.c:1257` | hashTypeDelete 移除 isSdsField 參數可能遺漏呼叫點 | 0.75 |
| ⚠️ | Major | `src/dict.c:902` | dictSetKeyAtLink 中新增的 validateStoredKeyConversion 呼叫可能造成效能影響 | 0.70 |
| 🔸 | Minor | `src/dict.c:97` | keyFromStoredKey 回呼的錯誤處理不足 | 0.60 |
| 🔸 | Minor | `src/dict.h:66` | __stored_key 巨集定義為空，可能降低可讀性 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未被使用</summary>

新增的 validateStoredKeyConversion 函式在整個 diff 中沒有被任何地方呼叫。這可能表示原本打算在關鍵路徑（例如 dictAddRaw 或 dictFindLinkInternal）加入驗證，但最後遺漏了。如果 keyFromStoredKey 回呼實作有誤，可能導致 key 轉換失敗而未被偵測，進而產生錯誤的 hash 或比較結果。建議在 dictAddRaw 或 dictFindLinkInternal 等進入點呼叫此函式，或移除該函式以避免 dead code。

**判斷依據**：diff 中新增了 validateStoredKeyConversion 函式，但搜尋整個 diff 未見任何呼叫點。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:1257</code> hashTypeDelete 移除 isSdsField 參數可能遺漏呼叫點</summary>

hashTypeDelete 的簽名從 `int hashTypeDelete(robj *o, void *key, int isSdsField)` 改為 `int hashTypeDelete(robj *o, void *key)`，移除了 isSdsField 參數。在 diff 中所有呼叫點都已更新，但若程式碼庫中其他檔案（未包含在此 diff）仍有使用舊簽名的呼叫，將導致編譯錯誤。建議全域搜尋確認所有呼叫點均已更新，或保留一個過渡版本。

**判斷依據**：diff 顯示 hashTypeDelete 的宣告和定義都移除了 isSdsField 參數，但無法確認所有呼叫點都在此 diff 中。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/dict.c:902</code> dictSetKeyAtLink 中新增的 validateStoredKeyConversion 呼叫可能造成效能影響</summary>

在 dictSetKeyAtLink 的錯誤處理路徑中，新增了 `validateStoredKeyConversion(d, key)` 呼叫。此函式會呼叫 keyFromStoredKey 回呼，若該回呼有非零成本（例如需要解包結構），且此路徑在正常操作中頻繁觸發，可能造成不必要的效能損耗。建議評估此驗證是否必要，或僅在 debug 模式啟用。

**判斷依據**：diff 中 dictSetKeyAtLink 的錯誤處理路徑新增了 validateStoredKeyConversion 呼叫，但該函式本身未被使用，且可能增加額外開銷。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:97</code> keyFromStoredKey 回呼的錯誤處理不足</summary>

dictStoredKey2Key 函式在 keyFromStoredKey 回呼存在時直接呼叫它，但沒有檢查回傳值是否為 NULL。如果回呼因某種原因回傳 NULL（例如 stored-key 格式錯誤），後續的 hash 或比較操作可能會對 NULL 指標進行操作，導致 crash。建議在 dictStoredKey2Key 中加入 NULL 檢查，或確保所有回呼實作都不會回傳 NULL。

**判斷依據**：diff 中新增的 dictStoredKey2Key 函式沒有對 keyFromStoredKey 的回傳值進行 NULL 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.h:66</code> __stored_key 巨集定義為空，可能降低可讀性</summary>

新增的 `#define __stored_key` 巨集展開為空，僅作為標記用途。雖然有助於程式碼閱讀，但對於不熟悉此慣例的開發者可能造成困惑。建議在註解中更清楚地說明其用途，或考慮使用其他方式（如 typedef）來標記 stored-key 指標。

**判斷依據**：diff 中新增了空的巨集定義，僅用於標記參數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12888 (cache hit 11904) ｜ completion tokens 1447 ｜ PR #1</sub>