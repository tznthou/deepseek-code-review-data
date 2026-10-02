<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並引入 `v2_enabled` 設定來切換 UI 版本。主要風險在於 `create_ui_app` 中 `static_subpath` 的指派邏輯相反，可能導致 V2 啟用時仍複製到 V1 路徑；此外，`v2_enabled` 預設為 `True` 會立即改變既有行為，且缺少對應的測試與文件更新。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:462` | V2 啟用時 static_subpath 指派錯誤 | 0.95 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | v2_enabled 預設為 True 可能造成非預期行為變更 | 0.90 |
| ⚠️ | Major | `src/prefect/server/api/server.py:462` | 變數指派邏輯不一致可能導致路徑錯誤 | 0.85 |
| 🔸 | Minor | `src/prefect/server/api/server.py:527` | 日誌訊息可能造成混淆 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:462</code> V2 啟用時 static_subpath 指派錯誤</summary>

在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`static_subpath` 被指派為 `prefect.__ui_static_subpath__`（V1 路徑），而 `source_static_path` 為 `prefect.__ui_v2_static_path__`。這導致後續 `create_ui_static_subpath` 將 V2 靜態檔案複製到 V1 的子路徑，可能覆蓋 V1 檔案或造成路徑混亂。建議將 `static_subpath` 改為 `prefect.__ui_v2_static_subpath__`。

**判斷依據**：diff 中 `if v2_enabled:` 區塊內 `static_subpath` 指派為 `prefect.__ui_static_subpath__`，而 `else` 區塊指派為 `prefect.__ui_v2_static_subpath__`，兩者相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> v2_enabled 預設為 True 可能造成非預期行為變更</summary>

新增的 `v2_enabled` 設定預設值為 `True`，這會讓所有現有使用者在升級後立即切換到實驗性 V2 UI，可能導致功能不穩定或破壞性變更。建議預設為 `False`，並在文件或升級指南中說明如何啟用。

**判斷依據**：diff 中 `default=True` 直接啟用 V2 UI，且描述標明為 experimental。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/api/server.py:462</code> 變數指派邏輯不一致可能導致路徑錯誤</summary>

`static_subpath` 的指派在兩個分支中與 `source_static_path` 不對稱：V2 分支使用 V1 的 subpath，V1 分支使用 V2 的 subpath。這顯示可能是複製貼上錯誤，應修正為各自對應的路徑。

**判斷依據**：diff 中兩個分支的 `static_subpath` 指派明顯相反。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/api/server.py:527</code> 日誌訊息可能造成混淆</summary>

在 `v2_enabled` 為 True 時記錄 "Serving experimental V2 UI"，但此訊息僅在 `os.path.exists(source_static_path)` 且 UI 啟用時輸出，若靜態檔案不存在則不會記錄，可能讓使用者誤以為 V2 未啟用。建議在設定讀取後立即記錄，或調整條件。

**判斷依據**：diff 中此日誌位於 `if (os.path.exists(source_static_path) and ...)` 區塊內。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5734 (cache hit 5632) ｜ completion tokens 1097 ｜ PR #8</sub>