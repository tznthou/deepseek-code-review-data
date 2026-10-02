<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 aof-load-broken 與 aof-load-broken-max-size 設定，允許在 AOF 檔案中間格式錯誤時自動截斷損壞部分。主要風險在於：1) 自動截斷可能造成資料遺失，且預設關閉但文件說明清楚；2) 在 loadAppendOnlyFiles 中，AOF_BROKEN_RECOVERED 的處理邏輯可能導致非最後一個檔案被截斷後仍繼續載入，造成資料不一致；3) 測試中使用了未定義的變數 $client，可能導致測試失敗。整體而言，功能立意良好，但需修正上述問題以確保正確性與測試可靠性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/aof.c:1722` | AOF_BROKEN_RECOVERED 在非最後一個檔案時未正確處理，可能導致資料不一致 | 0.95 |
| ⚠️ | Major | `tests/integration/aof.tcl:760` | 測試中使用了未定義的變數 $client | 0.90 |
| ⚠️ | Major | `src/aof.c:1728` | 自動截斷可能造成資料遺失，且未提供足夠的警告或備份機制 | 0.80 |
| 🔸 | Minor | `src/aof.c:1734` | truncate 後未更新 AOF 檔案大小相關的狀態 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/aof.c:1722</code> AOF_BROKEN_RECOVERED 在非最後一個檔案時未正確處理，可能導致資料不一致</summary>

在 loadAppendOnlyFiles 中，當 ret == AOF_BROKEN_RECOVERED 且 !last_file 時，程式碼將 ret 設為 AOF_FAILED 並記錄錯誤，但隨後在 if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) 的條件中，因為 ret 已被改為 AOF_FAILED，所以會進入 cleanup 並中止載入。然而，此處的邏輯有問題：如果 AOF_BROKEN_RECOVERED 發生在非最後一個檔案，實際上檔案已被 truncate 修改，但後續的檔案仍可能被載入，導致資料不一致。建議在非最後一個檔案遇到 AOF_BROKEN_RECOVERED 時，應立即中止載入並回報錯誤，且不應修改原始檔案。

**判斷依據**：diff 中 loadAppendOnlyFiles 的修改顯示，當 ret == AOF_BROKEN_RECOVERED 且 !last_file 時，ret 被改為 AOF_FAILED，但檔案已被 truncate，可能造成後續檔案載入時資料不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>tests/integration/aof.tcl:760</code> 測試中使用了未定義的變數 $client</summary>

在測試 'Append a new command after loading an incomplete AOF' 中，使用了 $client 變數，但該變數在此 scope 中並未定義。這會導致 Tcl 錯誤，使測試失敗。應先建立 client 連線，例如：set client [redis [srv host] [srv port] 0 $::tls]。

**判斷依據**：diff 中新增的測試區塊，該行直接使用 $client，但前文未定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1728</code> 自動截斷可能造成資料遺失，且未提供足夠的警告或備份機制</summary>

當 aof-load-broken 啟用且損壞部分小於 max-size 時，程式會直接 truncate 檔案，丟棄損壞部分之後的所有資料。這可能導致資料遺失，且僅記錄 warning。建議在 truncate 前先將原始檔案備份（例如複製一份），或至少提供更明確的警告，讓使用者知道有多少資料被丟棄。

**判斷依據**：diff 中 fmterr 處理區塊，直接呼叫 truncate 而無備份。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/aof.c:1734</code> truncate 後未更新 AOF 檔案大小相關的狀態</summary>

truncate 成功後，程式僅將檔案描述子 seek 到結尾，但未更新 server 中可能記錄的 AOF 檔案大小或 offset 等狀態。這可能導致後續 AOF 寫入時發生錯誤或覆蓋。建議檢查是否有相關狀態需要更新。

**判斷依據**：diff 中 truncate 成功後的處理，僅 seek 但未更新其他狀態。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6357 (cache hit 1536) ｜ completion tokens 1286 ｜ PR #7</sub>