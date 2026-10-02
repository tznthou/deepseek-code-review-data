<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並在伺服器端加入切換 V1/V2 的設定。主要風險在於 `create_ui_app` 中 `source_static_path` 與 `static_subpath` 的指派邏輯可能造成變數未定義或路徑錯誤，且 `v2_enabled` 預設為 True 可能導致未預期的行為變更。此外，Dockerfile 中安裝 Chromium 的步驟缺乏版本鎖定，可能影響供應鏈安全。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:458` | 變數指派邏輯錯誤：v2_enabled 為 False 時 static_subpath 未定義 | 0.95 |
| 🛑 | Blocker | `src/prefect/server/api/server.py:458` | v2_enabled 為 True 時 source_static_path 指向錯誤路徑 | 0.90 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | v2_enabled 預設為 True 可能造成未預期的行為變更 | 0.80 |
| 🔸 | Minor | `Dockerfile:70` | Chromium 安裝未鎖定版本，可能影響供應鏈安全 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:458</code> 變數指派邏輯錯誤：v2_enabled 為 False 時 static_subpath 未定義</summary>

在 `create_ui_app` 函式中，`static_subpath` 只在 `v2_enabled` 為 True 時被指派為 `prefect.__ui_static_subpath__`，但在 `v2_enabled` 為 False 的分支中，`static_subpath` 並未被指派，導致後續 `static_dir = prefect.settings.PREFECT_UI_STATIC_DIRECTORY.value() or str(static_subpath)` 會拋出 `NameError`。

**失敗情境**：當使用者設定 `PREFECT_SERVER_UI_V2_ENABLED=false` 且未設定 `PREFECT_UI_STATIC_DIRECTORY` 時，啟動伺服器會直接崩潰。

**建議修法**：在 `else` 分支中指派 `static_subpath = prefect.__ui_static_subpath__`，或將 `static_subpath` 的指派移到條件判斷之外。

**判斷依據**：diff 中 `else` 分支缺少 `static_subpath` 的指派，但後續程式碼使用 `static_subpath`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:458</code> v2_enabled 為 True 時 source_static_path 指向錯誤路徑</summary>

當 `v2_enabled` 為 True 時，`source_static_path` 被指派為 `prefect.__ui_v2_static_path__`，但該變數在 `src/prefect/__init__.py` 中定義為 `__module_path__ / "server" / "ui_v2"`，而 Dockerfile 中複製 V2 UI 的目標路徑為 `./src/prefect/server/ui-v2`（注意連字號 vs 底線）。這會導致 `os.path.exists(source_static_path)` 永遠為 False，V2 UI 無法被正確載入。

**失敗情境**：啟用 V2 UI 後，伺服器找不到靜態檔案，回傳 404 或空白頁面。

**建議修法**：統一命名，將 `__ui_v2_static_path__` 改為 `ui-v2` 或調整 Dockerfile 的複製目標。

**判斷依據**：`src/prefect/__init__.py` 中定義 `__ui_v2_static_path__ = __module_path__ / "server" / "ui_v2"`，而 Dockerfile 複製到 `ui-v2`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> v2_enabled 預設為 True 可能造成未預期的行為變更</summary>

新增的 `v2_enabled` 設定預設值為 `True`，這表示所有現有使用者升級後將預設使用實驗性的 V2 UI，而非原本的 V1 UI。這可能導致使用者介面出現未預期的變更或錯誤，尤其 V2 UI 仍標記為實驗性。

**建議修法**：將預設值改為 `False`，讓使用者明確選擇啟用 V2 UI。

**判斷依據**：diff 中 `default=True`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>Dockerfile:70</code> Chromium 安裝未鎖定版本，可能影響供應鏈安全</summary>

在 `ui-v2-builder` 階段中，`apt-get install chromium` 未指定版本，這會安裝最新版 Chromium。若未來 Chromium 出現重大變更或漏洞，可能導致建置失敗或引入安全風險。

**建議修法**：鎖定 Chromium 的版本，例如 `chromium=123.0.6312.86-1~deb11u1`。

**判斷依據**：diff 中 `chromium` 未指定版本。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7265 (cache hit 7168) ｜ completion tokens 1431 ｜ PR #8</sub>