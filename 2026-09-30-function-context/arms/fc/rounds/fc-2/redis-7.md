<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 aof-load-broken 與 aof-load-broken-max-size 設定，允許在 AOF 檔案中間發生格式錯誤時，若損壞部分小於指定大小則自動截斷並啟動。主要風險在於自動截斷可能造成資料遺失，且實作中對損壞大小的計算與錯誤處理有若干缺陷，可能導致誤判或未預期的行為。建議先修正 fmterr 處理中的大小計算與錯誤路徑，再考慮合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/aof.c:1724` | 損壞大小計算使用未更新的 sb.st_size，可能誤判 | 0.90 |
| ⚠️ | Major | `src/aof.c:1728` | truncate 失敗後未正確處理，可能導致資料不一致 | 0.80 |
| ⚠️ | Major | `src/aof.c:1680` | 成功截斷後未更新 sb.st_size，可能影響後續判斷 | 0.75 |
| ⚠️ | Major | `src/aof.c:1841` | AOF_BROKEN_RECOVERED 未在 loadAppendOnlyFiles 中正確處理 | 0.70 |
| 🔸 | Minor | `src/config.c:3258` | aof-load-broken-max-size 設定為 0 時可能導致意外行為 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/aof.c:1724</code> 損壞大小計算使用未更新的 sb.st_size，可能誤判</summary>

在 `fmterr` 處理中，使用 `sb.st_size` 來計算損壞部分大小，但 `sb` 是在函式開頭以 `redis_fstat` 取得的檔案大小，之後檔案可能已被修改（例如先前已執行過 `truncate`）。若檔案大小已改變，計算出的 `sb.st_size - valid_up_to` 將不準確，可能導致錯誤地截斷或拒絕截斷。建議改用 `ftello(fp)` 取得目前檔案位置，或重新取得檔案狀態。

**判斷依據**：diff 中新增的 fmterr 處理區塊使用了 `sb.st_size`，但 `sb` 來自函式開頭的 `redis_fstat`，且後續可能有 `truncate` 操作改變檔案大小。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1728</code> truncate 失敗後未正確處理，可能導致資料不一致</summary>

在 `fmterr` 處理中，若 `truncate` 失敗，程式僅記錄錯誤並繼續執行，最後仍會將 `ret` 設為 `AOF_FAILED` 並跳至 cleanup。但此時檔案可能已部分修改，且未嘗試恢復或提供更明確的錯誤訊息。建議在 truncate 失敗時立即設定 `ret = AOF_FAILED` 並跳至 cleanup，避免後續不必要的處理。

**判斷依據**：diff 中新增的 fmterr 處理區塊，truncate 失敗後僅記錄錯誤，未立即中斷流程。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1680</code> 成功截斷後未更新 sb.st_size，可能影響後續判斷</summary>

在成功截斷後，程式未更新 `sb.st_size`，若後續再次進入 `fmterr`（例如檔案中還有多處損壞），計算損壞大小時仍會使用舊的檔案大小，導致判斷錯誤。建議在截斷後重新取得檔案狀態或更新 `sb.st_size`。

**判斷依據**：diff 中成功截斷後未更新 `sb.st_size`，而後續仍可能使用該變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1841</code> AOF_BROKEN_RECOVERED 未在 loadAppendOnlyFiles 中正確處理</summary>

在 `loadAppendOnlyFiles` 中，當 `ret == AOF_BROKEN_RECOVERED` 且檔案不是最後一個時，程式會將 `ret` 設為 `AOF_FAILED` 並記錄錯誤，但之後的 `if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED)` 條件會再次進入 cleanup，可能導致重複處理或錯誤的返回值。建議釐清此處的邏輯，確保 `AOF_BROKEN_RECOVERED` 只在最後一個檔案時被接受。

**判斷依據**：diff 中新增的條件判斷，可能導致重複 cleanup。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/config.c:3258</code> aof-load-broken-max-size 設定為 0 時可能導致意外行為</summary>

`aof-load-broken-max-size` 的設定範圍為 0 到 LONG_MAX，若設為 0，則任何損壞大小都會被視為大於限制，導致無法自動修復。這可能是預期行為，但建議在文件中明確說明 0 的含義，或考慮將最小值設為 1。

**判斷依據**：diff 中新增的設定，最小值為 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 39276 (cache hit 39168) ｜ completion tokens 1481 ｜ PR #7</sub>