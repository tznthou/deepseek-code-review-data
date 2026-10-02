# CodeQL path-injection 25 / full-ssrf 2 分流 — 判準與預期表

> 定稿 2026-09-23T07:46:06Z —— **讀 SARIF 的 flow 與 code 之前**寫下, 之後不改。
> 標的: main `ff63650`, analysis `1823093375` (results 30 = open 27 + 已 dismiss 3)。

## 已知變因

- `threat-models: local` 把 argv / env / **檔案內容**都當汙染源 → 很多 flow 會是「argv 給路徑 → 讀檔 → 內容 → 另一個路徑」。**判定看值的最終來源, 不看最近的那個 source**
- 一筆 alert 可能有多個 source (`relatedLocations` 全列, `codeFlows` 可能只給代表路徑) → **全部 source 都看, 最差的那個決定判定**
- `.github/scripts/` 有兩個執行情境: 其他 repo 的 `04` (有 secret + `pull-requests: write`) 與本機 `review-local.sh` → 兩個都要算
- RESUME 記載「`04` 側 13 筆已逐行確認是 workflow 寫死的 argv/env」→ **不當前提, 重驗**
- 分流人 = 寫這些 code 的同一方 (自己改自己的考卷)

## 判準: 值的控制者 vs 執行者的權限

| 來源 | 控制者 | 判定 |
|---|---|---|
| workflow YAML 寫死的字面值 | kit / caller 維護者 | 信任 |
| reusable 的 `inputs` (caller 的 `with:`) | caller 維護者, 與 job 同權 | 信任 |
| `workflow_dispatch` inputs | 有 write 權限的人 (本來就能改 workflow) | 信任 |
| 本機 CLI 的 argv / env | 操作者本人 | 信任 |
| **`03` 產的 artifact (diff / `meta.json`)** | **PR 作者, 可能來自 fork** | **不信任** |
| **模型輸出 (`review.json` 的 path / line / body)** | **PR 內容可經 prompt injection 影響** | **不信任** |
| **外部資料 (AACR-Bench 資料集、`gh api` 抓的外部 diff)** | 第三方 | **不信任** (影響看執行情境) |

- 全部 source 都信任 → **won't fix**。不選 false positive: local threat model 是我們自己開的, CodeQL 對資料流的陳述是對的, 只是控制值的人本來就有同等以上的權限
- 有不信任的 source → 查 sink 有沒有被守衛擋住: 有 → 先用探針證明守衛有效, 才標 false positive; 沒有 → **成立**, 修 + 紅綠
- sink 只是「路徑字串被組出來」但沒有真的開檔 / 發請求 → 照實寫, 不因此降級

## 預期 (讀 flow 之前)

| alert | 位置 | 預期來源 | 預期判定 | 把握 |
|---|---|---|---|---|
| #27 | `deepseek_review.py:142` | argv 的 diff 路徑, 或 **diff 內容** (靠近 `select_rules`, #41 在 :145) | 不確定 | 低 |
| #28 | `deepseek_review.py:162` | 同上; 若是「diff 內容 → 規則檔路徑」就是不信任 | 不確定 | 低 |
| #29 | `deepseek_review.py:164` | 同上 | 不確定 | 低 |
| #30 | `deepseek_review.py:524` | argv 路徑 (讀輸入檔) | won't fix | 中 |
| #31 | `deepseek_review.py:526` | 同上 | won't fix | 中 |
| #32 | `deepseek_review.py:665` | argv 輸出路徑 | won't fix | 中 |
| #33 | `deepseek_review.py:667` | 同上 | won't fix | 中 |
| #34 | `deepseek_review.py:673` | 同上 | won't fix | 中 |
| #40 | `deepseek_review.py:225` (ssrf) | env `DEEPSEEK_BASE_URL` | won't fix | 高 |
| #35 | `post_review.py:186` | argv 路徑 | won't fix | 中 |
| #36 | `post_review.py:189` | 同上 | won't fix | 中 |
| #37 | `post_review.py:196` | argv 路徑; 或**模型輸出的 path** | 不確定 | 低 |
| #38 | `post_review.py:197` | 同上 | 不確定 | 低 |
| #17 | `check-dsh-version.py:36` | 本機 argv / env | won't fix | 中 |
| #18 | `check-dsh-version.py:47` | 同上 | won't fix | 中 |
| #19 | `check-dsh-version.py:73` | 同上 | won't fix | 中 |
| #20 | `check-dsh-version.py:76` | 同上 | won't fix | 中 |
| #22 | `check-dsh-version.py:102` | 同上 | won't fix | 中 |
| #14 | `build_eval_set.py:51` | env / 常數目錄 | won't fix | 低 |
| #15 | `build_eval_set.py:53` | 同上 | won't fix | 低 |
| #16 | `build_eval_set.py:58` | 同上 | won't fix | 低 |
| #21 | `build_eval_set.py:148` | **資料集欄位 (repo 名 / PR 編號) 組成路徑** | 可能成立 | 低 |
| #23 | `eval_filter.py:158` | dispatch 的 `--filter-prompt` | won't fix | 中 |
| #24 | `eval_filter.py:160` | 同上 | won't fix | 中 |
| #25 | `eval_filter.py:230` | argv / 常數的輸出路徑 | won't fix | 中 |
| #26 | `eval_filter.py:233` | 同上 | won't fix | 中 |
| #39 | `eval_filter.py:56` (ssrf) | env 的 base URL | won't fix | 中 |

**總預期**: won't fix ≥ 21 筆; 成立候選 0–6 筆, 集中在三處 —— `deepseek_review.py:142-164` (diff 內容 → 路徑?)、`post_review.py:196-197` (模型輸出 → 路徑?)、`build_eval_set.py:148` (資料集欄位 → 路徑?)。
