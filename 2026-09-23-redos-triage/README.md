# CodeQL polynomial-redos 4 筆的分流 — 2026-09-23 (第十五輪)

> ⚠️ 預期表都在跑之前定稿, 跑完沒有修改 (檔內有定稿時間)。
> 量的是 **修正前** 的 code (main `f090e1e`)。現在的 `locate.py` 已經是 `_corner_quoted()` 迴圈,
> 重跑 `redos_bench.py` 的 `43_real` 會是線性 —— 要重現平方, 先 `git show f090e1e:.github/scripts/locate.py`。

## 結論

| alert | 位置 | 判定 | 關鍵數字 |
|---|---|---|---|
| #41 | `deepseek_review.py:145` | false positive (已 dismiss) | 16 MB 4 ms; 拿掉 `re.M` → 平方 |
| #42 | `locate.py:57` | false positive (已 dismiss) | 16 MB 13 ms; 餵沒切行的字串 → 平方 |
| #44 | `post_review.py:68` | false positive (已 dismiss) | 同 #42 |
| #43 | `locate.py:143` | **成立**, PR #27 修掉, main 上已 fixed | 64K 字元 5.4 s / 128K 21.7 s → 0.04 ms |

## 檔案

| 檔 | 內容 |
|---|---|
| `redos-expectations.md` | 量測預期表 (8 case, 含 4 個對照組), 定稿 05:30 UTC |
| `redos_bench.py` | 量測 harness: 呼叫 repo 真正的函式, 每個 case 子行程跑、120 s 逾時, 翻倍看比值 |
| `redos-results.json` | 量測結果 (本機 Python 3.13 / arm64) |
| `alerts.tsv` | main 上 31 筆 open alert 當時的清單 (number / tool / rule / severity / ref / path / line / created) |
| `fix43_check.py` | 修法候選的等價性 (隨機 30 萬筆) 與時間檢查 (早期的「砍尾巴」版本; 最終採用 `str.find` 迴圈, 用同一套比對重驗過) |
| `redgreen-expectations.md` | selftest 紅綠預期表, 定稿 05:50 UTC |
| `st-new.out` / `st-old.out` | 紅綠實際輸出: 新版 93 PASS; 舊版 91 PASS + 2 FAIL (兩個時間探針各 5.4 s) |
| `probe-expectations.md` | v1.3.1 發版後 probe 回歸的預期表 (7 項), 實跑 7/7 |
| `dismiss-4{1,2,4}.json` | 三筆 false positive 的 dismiss request body (含理由原文) |

## 方法 (可重用在下一批 ReDoS alert)

1. alert 訊息給攻擊字串形狀 ("strings starting with X and many repetitions of Y"), SARIF 的 `relatedLocations` 給 source
2. 用真正的函式量, 輸入翻倍: 比值 ≈2 線性 / ≈4 平方; 每個 case 帶結果合理性檢查, 確認走到要測的路徑
3. **每筆配一個拿掉保護上下文的對照組** —— 對照組變平方才算證明了「為什麼安全」
