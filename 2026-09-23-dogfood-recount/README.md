# 09-22 dogfood 重數 — 2026-09-23

> README §4.8 原寫「2026-09-22 的四次 dogfood：4 筆 finding、0 筆成立」。
> 從 `04` 的 log 逐次撈回來是**三個 PR、五次 run、7 筆 finding**, 「0 筆成立」不變。
> 更正在 PR #30 (main `12bc089`)。時間皆 UTC。

## 結論: #21 的第二、三次 run 被記成一次

| PR | kit 版本 (`HEAD is now at`) | `04` run | 時間 (09-22) | findings | 成立 |
|---|---|---|---|---|---|
| #20 | `6a08eab` | 35686799012 | 04:25 | 0 | — |
| #21 第一次 (`0015787`) | `6a08eab` | 35688569119 | 04:53 | exit 2 (解析失敗) | — |
| #22 (`0b1f464`) | `6a08eab` | 35689137333 | 05:02 | 1 | 0 |
| #21 第二次 (`12ce9a6`, docs) | `6a08eab` | 35690008749 | 05:15 | 3 | 0 |
| #21 第三次 (`8d5fdd3`, merge main) | `6a08eab` | 35690263940 | 05:19 | 3 | 0 |

README 原本的三種失效模式分別出自**兩次** run (下面的 b、e、d), 筆數卻只記了一次的 3 → a、c、f 從沒被記錄。

## #21 兩次 run 的 findings (本目錄 `pr21-runs/`)

第二次 `12ce9a6`:
- **a** `reusable-ai-review-post.yml:188` major 0.8「`REVIEW_BLOCKED_TERMS` 可能未正確傳遞至 Python 腳本」— **不成立**: Python 端 `load_blocked_terms(os.environ.get("REVIEW_BLOCKED_TERMS"))` 就在同一份 diff (`0015787` 加入, `gh api commits/0015787` 的 patch 確認), diff 19,392 字元沒有截斷; 同日真實 CI 也實測到攔截生效。它自己的 evidence 寫「未顯示後續 `run` 區塊如何使用該變數」。定位層以「片段多重命中 (2 處), 不猜」擋下, 沒貼 inline
- **b** `deepseek_review.py:190` minor 0.7「load_blocked_terms 對輸入型別假設過強」(bytes) — README 失效模式 1
- **c** `deepseek_review.py:210` minor 0.6「blocked_terms_hits 對 sections 的值未處理 None」— **不成立**: `(text or "")` 已處理, 唯一的呼叫點傳進來的兩個區段 (system prompt、user message) 都是 `str`

第三次 `8d5fdd3`:
- **d** `reusable-ai-review-post.yml:188` major 0.9「secret 傳遞方式可能導致值未正確遮蔽」— README 失效模式 3; 同樣被定位層擋下
- **e** `deepseek_review.py:211` minor 0.7「blocked_terms_hits 效能問題」(先轉小寫、Aho-Corasick) — README 失效模式 2
- **f** `deepseek_review.py:190` minor 0.6「load_blocked_terms 未處理可能的編碼問題」— **不成立**, 見下方實跑

### f 的實跑 (本機 Python 3.13, 在 repo 根目錄)

```bash
REVIEW_BLOCKED_TERMS=$'abc\xff\xfedef\n# comment\nxyz' python3 -c "
import os, sys
sys.path.insert(0, '.github/scripts')
import deepseek_review as d
raw = os.environ.get('REVIEW_BLOCKED_TERMS')
print(type(raw).__name__, repr(raw))
terms, ignored = d.load_blocked_terms(raw)
print(terms, ignored)
print(d.blocked_terms_hits({'diff': 'x ABC' + raw.split(chr(10))[0][3:] + 'DEF y', 'other': 'nothing'}, terms))
"
```

結果: `str 'abc\udcff\udcfedef\n# comment\nxyz'` → terms 2 條、ignored 0 → hits `[('diff', 1)]`, **沒有例外**。
環境變數裡的非法位元組會變成 surrogate, 字串操作照常。

## `v1.3.0` 到 `v1.3.1` (#23–#28)

| PR | kit 版本 | `04` run | 時間 | findings | 成立 |
|---|---|---|---|---|---|
| #23 發版 `v1.3.0` | — | 35690636479 | 09-22 05:25 | **startup_failure** (README §7 的兩分鐘破窗) | — |
| #24 docs | `456c175` | 35691642162 | 09-22 05:40 | 0 | — |
| #25 docs | `456c175` | 35692239935 | 09-22 05:49 | 0 | — |
| #26 docs | `456c175` | 35756192734 | 09-22 16:45 | 0 | — |
| #27 第一次 | `456c175` | 35824279182 | 09-23 05:53 | 2 (relocated 2) | **1** |
| #27 第二次 | `456c175` | 35824504834 | 09-23 05:56 | 0 | — |
| #28 發版 `v1.3.1` | `456c175` | 35825064776 | 09-23 06:04 | 0 | — |

#27 成立的是 `tools/selftest.py:16` 的 `ROOT =pathlib.Path(...)` (編輯時結尾空格被吃掉); 不成立的是 `:520` 時間探針「在 CI 可能 flaky」(selftest 不在 CI 跑, 修正後 128K 字元 0.04 ms, 離 0.5 s 門檻四個數量級)。

## 查法 (可重跑)

1. `gh run list --workflow "04 ai review post"` → 每個 run 的 log grep `PR #N`、`findings=`、`HEAD is now at`; **一次 run 一行, 不從 PR 頁面數** (一個 PR 可以有多次 run)
2. `gh run download <run-id> -n ai-review-output` 取 `findings.json` —— retention 7 天, 09-22 那批 09-29 過期, 本目錄已存兩份
3. ⚠️ `03` 的 `ai-review-input` (含 diff) 已下載不到 (`No valid artifacts found`), diff 內容改用 `gh api repos/O/R/commits/<sha>` 的 patch 確認
4. 每個 `04` run 對應哪個 commit: log 裡 `commits/<40 位 sha>/pulls` 那行
