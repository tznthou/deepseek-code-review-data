<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 V2 UI 的建置與服務整合，包含 Dockerfile 多階段建置、Python 設定與伺服器路由切換。主要風險在於 V2 UI 預設啟用（v2_enabled 預設 True）可能導致未預期的行為變更，且缺少對應的測試驗證。另有 GitHub Actions workflow 中直接複製建置產物至原始碼樹，可能造成 CI 環境的污染。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | V2 UI 預設啟用可能造成未預期的行為變更 | 0.80 |
| ⚠️ | Major | `src/prefect/server/api/server.py:462` | V2 啟用時 static_subpath 誤用 V1 路徑 | 0.75 |
| 🔸 | Minor | `.github/workflows/python-package.yaml:51` | CI 中直接複製建置產物至原始碼樹可能造成污染 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> V2 UI 預設啟用可能造成未預期的行為變更</summary>

新增的 `v2_enabled` 設定預設為 `True`，這表示升級後所有使用者將預設使用實驗性的 V2 UI，而非原本的 V1 UI。若 V2 UI 尚未穩定或與現有功能不相容，可能導致使用者遇到問題。建議將預設值改為 `False`，或提供明確的遷移指引。

**判斷依據**：diff 中新增的設定欄位，default=True。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/api/server.py:462</code> V2 啟用時 static_subpath 誤用 V1 路徑</summary>

在 `v2_enabled` 為 True 的分支中，`static_subpath` 被指派為 `prefect.__ui_static_subpath__`（V1 的動態子路徑），而非 V2 的 `prefect.__ui_v2_static_subpath__`。這可能導致 V2 UI 的靜態檔案被複製到錯誤的位置，或與 V1 衝突。

**判斷依據**：diff 中 `static_subpath = prefect.__ui_static_subpath__` 位於 v2_enabled 分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/workflows/python-package.yaml:51</code> CI 中直接複製建置產物至原始碼樹可能造成污染</summary>

在 workflow 中執行 `cp -r dist ../src/prefect/server/ui-v2` 會將建置產物複製到原始碼樹中。若後續步驟未清理，可能導致 git diff 檢查失敗或將產物意外提交。建議改為將產物輸出至暫存目錄，或確保後續步驟會清理。

**判斷依據**：diff 中新增的 cp 指令。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15491 (cache hit 15488) ｜ completion tokens 804 ｜ PR #8</sub>