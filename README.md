# deepseek-code-review 實測原始資料

[deepseek-code-review](https://github.com/tznthou/deepseek-code-review) 這個 kit 對自己做過的量測，原始資料放在這裡：
模型的 review 輸出、標記單、計分結果、腳本，以及實驗當下寫的筆記。

整理過的結論在主 repo 的[實測紀錄](https://github.com/tznthou/deepseek-code-review/tree/main/experiments)，
**數字以那邊的頁面為準**；這裡是讓人回頭查證用的。

## 怎麼讀

- 一個實驗一個目錄，目錄名是「日期－主題」，跟主 repo 實測紀錄的頁面對應
- 每個目錄先看 `README.md`（`2026-09-21-flash-3x` 看 `RESULTS.md`）。那是實驗當下的筆記，用語比較口語，
  也會提到當時的計畫檔、交接文件與其他內部紀錄——**那些不在這裡**
- 腳本的路徑照原本的位置寫（`<repo>/.claude/experiments/<目錄>/`），**不保證拿來就能重跑**
- 模型輸出是 API 回應的原文。標記單的判讀者是人還是語言模型、有沒有盲標，見各目錄的 README

## 公開前做了什麼

- 本機路徑換成 `<repo>/`、`~/`
- 牽涉 private repo 的名稱換成「另一個專案（private repo）」；那個 repo 的端到端驗收紀錄整個不放
- 少數幾處文字改寫：私有工具的名稱換成功能描述、一次 key 設定錯誤的描述拿掉細節
- API 認證失敗時，錯誤訊息回顯的 key 末幾碼一律遮成 `****[遮蔽]`
- `2026-09-21-three-way-review/codex-full.txt` 檔頭加註出處（改寫自 Apache-2.0 授權的 prompt）
- 第三方資料集不重新散布，見 [NOTICE.md](NOTICE.md)
- 每次匯出都跑同一組檢查：symlink、二進位檔、私有名稱與路徑、gitleaks、檔案數對帳

## 目錄

| 目錄 | 問了什麼 | 結論 |
|---|---|---|
| `2026-09-21-flash-3x` | 「不要用 flash」換一種語言還成不成立 | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-09-21-flash-3x.md) |
| `2026-09-21-three-way-review` | 三個 reviewer（`deepseek-v4-pro`、`deepseek-flash`、Codex）看同一份標的，召回與定位差多少 | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-09-21-three-way-review.md) |
| `2026-09-23-dogfood-recount` | 本 repo 自己的 PR 上，AI review 報的 finding 重數一次 | [實測紀錄索引](https://github.com/tznthou/deepseek-code-review/tree/main/experiments) |
| `2026-09-23-path-ssrf-triage` | CodeQL 的 path／SSRF 告警怎麼分流（沒有呼叫模型） | 同上 |
| `2026-09-23-redos-triage` | CodeQL 的 ReDoS 告警哪些是真的（沒有呼叫模型） | 同上 |
| `2026-09-24-actions-policy` | caller 的 Actions 政策會不會擋掉 kit | 同上 |
| `2026-09-24-confidence-loop` | 模型自報的信心值，分不分得出對錯；`rounds/ph-*` 是 `2026-10-01-prompt-hygiene` 的輸出（共用同一套跑法） | 同上 |
| `2026-09-24-v1.4.0-regression` | v1.4.0 發版後的回歸 | 同上 |
| `2026-09-25-line-refs` | 文件裡寫死的行號還準不準 | 同上 |
| `2026-09-25-qodo-bench` | 修改型 PR 上抓得到幾成 | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-09-25-qodo-bench.md) |
| `2026-09-25-self-consistency-sim` | 同一份 diff 跑幾次再投票，划不划算（重算既有輸出，沒有呼叫 API） | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-09-25-self-consistency-sim.md) |
| `2026-09-26-rules-loop` | 把 repo 規範給它，規則類抓得多嗎、代價是什麼 | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-09-26-rules-loop.md) |
| `2026-09-26-v1.4.1` | 強制第三方 action 釘 SHA 的 caller 能不能用 | [實測紀錄索引](https://github.com/tznthou/deepseek-code-review/tree/main/experiments) |
| `2026-09-28-cache-probe` | 規範那次呼叫為什麼吃不到快取 | 同上 |
| `2026-09-28-v140-exit` | v1.4.0 的信心改動，在修改型 PR 上有沒有讓行內留言漏掉更多真問題 | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-09-28-v140-exit.md) |
| `2026-09-28-v150-repo-rules` | v1.5.0 `repo-rules-path` 的驗證與回歸 | [實測紀錄索引](https://github.com/tznthou/deepseek-code-review/tree/main/experiments) |
| `2026-09-28-v160-inline` | v1.6.0「預設只貼摘要」的回歸 | 同上 |
| `2026-09-30-function-context` | 把改動所在的整個函式一起送，抓得比較多嗎 | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-09-30-function-context.md) |
| `2026-10-01-claim-reach` | 用 grep 反駁 finding 的說法，能刷掉多少誤報（沒有呼叫 DeepSeek） | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-10-01-claim-reach.md) |
| `2026-10-01-prompt-hygiene` | rubric 的兩個已知問題，該不該改 | [頁面](https://github.com/tznthou/deepseek-code-review/blob/main/experiments/2026-10-01-prompt-hygiene.md) |

## 沒放的東西

| 目錄 | 沒放的東西 | 數量 | 原因 | 怎麼取得或重建 |
|---|---|---|---|---|
| 2026-09-24-confidence-loop | `__pycache__` | 4 | Python 快取 | — |
| 2026-09-24-confidence-loop | `backup` | 2 | 迭代過程的備份 | — |
| 2026-09-24 外部 repo 端到端驗收 | 整個目錄 | 7 | 外部 private repo 的端到端驗收（對話紀錄、session ID），永不公開；結論會寫進主 repo 實測紀錄的工程驗證段 | — |
| 2026-09-25-qodo-bench | `__pycache__` | 2 | Python 快取 | — |
| 2026-09-25-qodo-bench | `cal.log` | 4 | cal.com 各個 PR 的 log 寫進了同一個檔、互相覆蓋（`Path.with_suffix` 把 `.com-N` 當成副檔名），只剩最後寫入的那一份，留著會誤導 | — |
| 2026-09-25-qodo-bench | `data/bench.jsonl` | 1 | 第三方資料集 Qodo PR-Review-Bench（MIT）原檔 | `scripts/fetch_prs.py` 下載（revision 見 `data/revision.txt`） |
| 2026-09-25-qodo-bench | `data/rules_for_repo.jsonl` | 1 | 第三方資料集 Qodo PR-Review-Bench（MIT）原檔 | `scripts/fetch_prs.py` 下載（revision 見 `data/revision.txt`） |
| 2026-09-25-qodo-bench | `evalset.json` | 1 | 從 Qodo PR-Review-Bench 產生的評估集（內容多半是資料集原文） | `scripts/build_evalset.py` |
| 2026-09-25-qodo-bench | `prs` | 301 | Qodo PR 的 diff 與 metadata | `scripts/fetch_prs.py`（照 `data/revision.txt` 釘的 revision 重抓） |
| 2026-09-25-qodo-bench | `report-src` | 4 | 本機 HTML 報告的原始檔（套用本機範本、內文引用內部紀錄） | 結論見主 repo 實測紀錄的 qodo-bench 頁 |
| 2026-09-25-self-consistency-sim | `__pycache__` | 1 | Python 快取 | — |
| 2026-09-26-rules-loop | `__pycache__` | 4 | Python 快取 | — |
| 2026-09-26-rules-loop | `backup` | 2 | 迭代過程的備份 | — |
| 2026-09-26-rules-loop | `.DS_Store` | 1 | macOS 系統檔 | — |
| 2026-09-26-rules-loop | `cal.log` | 16 | cal.com 各個 PR 的 log 寫進了同一個檔、互相覆蓋（`Path.with_suffix` 把 `.com-N` 當成副檔名），只剩最後寫入的那一份，留著會誤導 | — |
| 2026-09-26-rules-loop | `balance-d1-start.json` | 1 | API 帳戶餘額 | — |
| 2026-09-26-rules-loop | `balance-start.json` | 1 | API 帳戶餘額 | — |
| 2026-09-26-rules-loop | `guard-targets.sha256` | 1 | 本機檔案的 checksum 清單，只對本機的 `guard.py` 有意義 | — |
| 2026-09-26-v1.4.1 | `probe-orig` | 3 | probe repo 檔案改動前的原樣備份 | — |
| 2026-09-28-cache-probe | `__pycache__` | 1 | Python 快取 | — |
| 2026-09-28-v150-repo-rules | `anonymize-backup` | 5 | 匿名化之前的原文備份 | — |
| 2026-09-28-v150-repo-rules | `probe-orig` | 3 | probe repo 檔案改動前的原樣備份 | — |
| 2026-09-28-v150-repo-rules | `scripts/anonymize_github_texts.py` | 1 | 一次性腳本，內容就是要替換掉的私有名稱 | — |
| 2026-09-28-v160-inline | `probe-orig` | 3 | probe repo 檔案改動前的原樣備份 | — |
| 2026-09-30-function-context | `.DS_Store` | 1 | macOS 系統檔 | — |
| 2026-09-30-function-context | `cal.log` | 3 | cal.com 各個 PR 的 log 寫進了同一個檔、互相覆蓋（`Path.with_suffix` 把 `.com-N` 當成副檔名），只剩最後寫入的那一份，留著會誤導 | — |
| 2026-09-30-function-context | `prs` | 702 | diff（Qodo PR 的原始版本，與擴到所在函式的版本） | `scripts/build_diffs.py` 從 Qodo PR 的公開 fork 抓 base／head 重新產生 |
| 2026-09-30-function-context | symlink | 402 | symlink（目標是本機絕對路徑） | 指向同一批資料的捷徑，資料本身見對應目錄或排除表 |
| 2026-10-01-claim-reach | `__pycache__` | 1 | Python 快取 | — |
| 2026-10-01-claim-reach | `data/dataset.json` | 1 | 第三方資料集 AACR-Bench（Apache-2.0）原檔 | Hugging Face `Alibaba-Aone/aacr-bench`，sha256 見 NOTICE.md |
| 2026-10-01-claim-reach | `out/reach.csv` | 1 | 逐列帶 AACR comment 原文（760 筆），等於資料集的副本 | `scripts/reach.py` 從 `dataset.json` 重算（不呼叫 API） |
| 2026-10-01-prompt-hygiene | `__pycache__` | 1 | Python 快取 | — |

## 授權

我們自己的產出：MIT，見 [LICENSE](LICENSE)。第三方資料集與改寫自第三方的檔案，見 [NOTICE.md](NOTICE.md)；
Apache-2.0 全文見 [LICENSE-Apache-2.0.txt](LICENSE-Apache-2.0.txt)。
