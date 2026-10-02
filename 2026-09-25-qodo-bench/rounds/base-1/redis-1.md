<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 dict 的 stored-key API 從全域狀態切換（dictUseStoredKeyApi）改為透過 keyFromStoredKey 回呼函式，以消除脆弱的狀態管理。整體方向合理，但存在一個重大正確性問題：dictSetKeyAtLink 在 newItem=0 時使用 addedKey 而非原始 key 進行查找，可能導致找不到既有 entry 而觸發 assert。此外，validateStoredKeyConversion 函式未被使用，且 dictGetHash 的註解可能誤導。建議先修正 dictSetKeyAtLink 的查找鍵值問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/dict.c:914` | dictSetKeyAtLink 在 newItem=0 時使用 addedKey 查找可能失敗 | 0.90 |
| 🔸 | Minor | `src/dict.c:102` | validateStoredKeyConversion 函式未被使用 | 0.80 |
| 🔸 | Minor | `src/dict.c:1807` | dictGetHash 的註解可能誤導 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/dict.c:914</code> dictSetKeyAtLink 在 newItem=0 時使用 addedKey 查找可能失敗</summary>

在 dictSetKeyAtLink 中，當 newItem=0 且 *link 為 NULL 時，程式碼使用 addedKey 呼叫 dictFindLink。但 addedKey 是經過 keyDup 處理後的鍵，可能與原始 key 不同（例如 keyDup 可能複製或轉換鍵）。如果 dictFindLink 使用 addedKey 找不到對應的 entry，則會觸發 assert(*link != NULL) 失敗。

失敗情境：當 dictType.keyDup 非 NULL 且會改變鍵的內容（例如複製 sds 或進行其他轉換），且呼叫者傳入的 key 與儲存的鍵不同時，dictFindLink 將無法找到 entry。

建議：應使用原始 key（或 dictStoredKey2Key(d, key)）進行查找，而不是 addedKey。

**判斷依據**：diff 中此行將原本的 `*link = dictFindLink(d, key, NULL);` 改為 `*link = dictFindLink(d, addedKey, NULL);`，但 addedKey 是 `d->type->keyDup(d, key)` 的結果，可能與原始 key 不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:102</code> validateStoredKeyConversion 函式未被使用</summary>

新增的 validateStoredKeyConversion 函式在整個 diff 中沒有被呼叫。這可能是未完成的功能或遺留的除錯程式碼。

建議：如果不需要，應移除此函式；如果需要，應在適當的地方呼叫它。

**判斷依據**：diff 中新增了此函式，但搜尋整個 diff 未發現任何呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/dict.c:1807</code> dictGetHash 的註解可能誤導</summary>

新增的註解「Compiler inlines this for internal calls within dict.c (verified with -O3)」可能不準確，因為編譯器是否內聯取決於多種因素，且此函式是全域函式，可能被外部呼叫。

建議：移除或修正此註解，避免誤導。

**判斷依據**：diff 中新增了此註解，但無法驗證其正確性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11911 (cache hit 1536) ｜ completion tokens 882 ｜ PR #1</sub>