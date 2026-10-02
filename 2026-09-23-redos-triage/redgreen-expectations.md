# #43 紅綠預期表 — 定稿 2026-09-23T05:50:53Z (跑之前, 之後不改)

只替換 .github/scripts/locate.py (git checkout HEAD --), selftest 保持新版。

| 跑的 locate.py | [1]~[15] 舊 86 項 | [16] 前五項 (結果沒變) | [16] 後兩項 (0.5 s 內) | 總計 / exit |
|---|---|---|---|---|
| 新版 | 86 PASS | 5 PASS | 2 PASS | 93 PASS / exit 0 |
| 舊版 | 86 PASS | 5 PASS | **2 FAIL** (各約 5 s) | 91 PASS + 2 FAIL / exit 1 |

組數: grep -c '^\[[0-9]' → 16

不符時的意義:
- 舊版前五項有 FAIL → 那幾項不是「兩版都該過」的探針, 我對等價的理解有誤
- 舊版後兩項 PASS → 時間探針抓不到這個 bug (門檻或形狀錯)
- 新版任何 FAIL → 修法有問題
