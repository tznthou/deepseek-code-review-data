#!/usr/bin/env python3
"""預期表定稿前，實際執行每一個埋點：缺陷要真的出事，陷阱要真的已經處理好。

09-21 的 B2 探針就是沒實跑、前提錯了一整天才發現（log 存在但沒有非空白行時
total 會是兩行 0）。這支把 release_notes.py 的每一格都跑一次，任何一格跟預期
不符就 exit 1。臨時 git repo 建在 scratchpad，不碰 /tmp。
"""
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "targets/src/sandbox/release_notes.py"
SCRATCH = os.environ.get("SCRATCH_DIR")

spec = importlib.util.spec_from_file_location("release_notes", SRC)
rn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rn)

failures = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS  " if ok else "FAIL  ") + name + (f"  ｜ {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def git(repo: str, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout


def run_main(argv: list[str], env: dict) -> tuple[int, str, str]:
    err, out = io.StringIO(), io.StringIO()
    with mock.patch.object(sys, "argv", ["release_notes.py", *argv]), \
         mock.patch.dict(os.environ, env, clear=False), \
         redirect_stderr(err), mock.patch("sys.stdout", out):
        code = rn.main()
    return code, err.getvalue(), out.getvalue()


with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
    repo = os.path.join(tmp, "repo")
    os.mkdir(repo)
    git(repo, "init", "-q")
    git(repo, "commit", "-q", "--allow-empty", "-m", "feat: 第一版")
    git(repo, "tag", "v1.0.0")
    git(repo, "commit", "-q", "--allow-empty", "-m", "feat(api): 新增端點")
    git(repo, "commit", "-q", "--allow-empty", "-m", "fix: 修正時區")
    git(repo, "commit", "-q", "--allow-empty", "-m", "chore: 升級相依")
    git(repo, "tag", "v1.1.0")
    git(repo, "tag", "v1.1.1")  # 跟 v1.1.0 同一個 commit：範圍內沒有新 commit
    dead = "http://127.0.0.1:9/services/T000/B000/SECRETTOKEN"
    env = {"NOTES_WEBHOOK": dead, "NOTES_MAX": ""}

    # ── A 類：真缺陷 ──────────────────────────────────────────
    code, err, _ = run_main([repo, "v1.0.0"], env)
    check("PA1 第一個 tag 的 prev 變成最後一個 tag，靜默回 0",
          code == 0 and "v1.1.1..v1.0.0 之間沒有新 commit" in err, err.strip())
    check("PA1 對照：v1.0.0 本身其實有 commit",
          len(rn.commits_between(repo, "v1.0.0~0^{tree}", "v1.0.0")) >= 0
          and git(repo, "log", "--format=%s", "v1.0.0").strip() == "feat: 第一版")

    err_buf = io.StringIO()
    with redirect_stderr(err_buf):
        ok = rn.post(dead, "x")
    check("PA2 post 失敗時把含 token 的 webhook URL 整段寫進 log",
          ok is False and "SECRETTOKEN" in err_buf.getvalue(), err_buf.getvalue().strip())

    grouped = dict(rn.group([("a1", "feat(api): 新增端點"), ("b2", "fix: 修正")]))
    check("PA3 帶 scope 的 conventional commit 被分到「其他」",
          any("feat(api)" in x for x in grouped.get("其他", [])), str(grouped))

    # ── B 類：陷阱（都已經處理好）─────────────────────────────
    check("PB1 tag 先過 regex，含 ; 的 tag 直接回 2",
          run_main([repo, "v1.0.0; rm -rf /"], env)[0] == 2)

    missing = rn.load_config(os.path.join(tmp, "nope.json"))
    bad = os.path.join(tmp, "bad.json")
    pathlib.Path(bad).write_text("{oops", encoding="utf-8")
    try:
        rn.load_config(bad)
        raised = False
    except SystemExit as e:
        raised = "不是合法的 JSON" in str(e)
    check("PB2 設定檔不存在回 {}、壞 JSON 以明確訊息結束", missing == {} and raised)

    with mock.patch.dict(os.environ, {"NOTES_MAX": "abc"}), redirect_stderr(io.StringIO()) as w:
        v = rn.max_items()
    check("PB3 NOTES_MAX 不是整數 → 警告並用預設值", v == rn.DEFAULT_MAX and "不是整數" in w.getvalue())

    fake = subprocess.CompletedProcess([], 0, stdout="nospace\nabc123 feat: x\n", stderr="")
    with mock.patch.object(rn.subprocess, "run", return_value=fake):
        parsed = rn.commits_between(repo, "a", "b")
    check("PB4 沒有空白的行先跳過，split 不會 unpack 失敗", parsed == [("abc123", "feat: x")], str(parsed))

    check("PB5 未知前綴一律歸 other，不會 KeyError",
          dict(rn.group([("c3", "chore: y"), ("d4", "沒有冒號的標題")])).get("其他") is not None)

    rn.render("t", [("新功能", ["a"])])
    rn.render("t", [("修正", ["b"])])
    check("PB6 render 的預設 footer 從沒被修改", rn.render.__defaults__ == ([],), str(rn.render.__defaults__))

    code, err, out = run_main([repo, "v1.1.0"], env)
    check("PB7 post 失敗回 False，main 檢查後回 1、不印公告", code == 1 and out == "", f"code={code}")

    check("PB8 不重試是註解寫明的刻意決定", "# 不重試：" in SRC.read_text(encoding="utf-8"))

    code, err, _ = run_main([repo, "v1.1.1"], env)
    check("PB9 範圍內沒有 commit 時在 commits[0] 之前就 return 0",
          code == 0 and "之間沒有新 commit" in err, err.strip())

    check("PB10 docstring 的 URL 是範例佔位字串", "T000/B000/XXXX" in SRC.read_text(encoding="utf-8"))

    # ── 附帶：預登記為「報了算成立」的真問題 ────────────────
    with mock.patch.dict(os.environ, {"NOTES_MAX": "-1"}):
        n = len(rn.commits_between(repo, "v1.0.0", "v1.1.0")[: rn.max_items()])
    check("X1 NOTES_MAX=-1 會靜默丟掉最舊的一筆", n == 2, f"3 筆剩 {n}")

    proc = subprocess.run(["git", "log", "v9.9.9..v1.0.0"], cwd=repo, capture_output=True, text=True)
    check("X2 git log 失敗（不存在的 tag）被當成沒有 commit",
          proc.returncode != 0 and rn.commits_between(repo, "v9.9.9", "v1.0.0") == [], f"rc={proc.returncode}")

    notgit = os.path.join(tmp, "notgit")
    os.mkdir(notgit)
    try:
        rn.list_tags(notgit)
        crashed = False
    except subprocess.CalledProcessError:
        crashed = True
    check("X3 repo 路徑不是 git repo 時直接拋 CalledProcessError（traceback）", crashed)

    # X4：連得上但不回應 → getresponse() 讀取逾時丟 TimeoutError，不是 URLError。
    # 另外確認 HTTPError（4xx/5xx）是 URLError 的子類別，會被接住——報「沒接 HTTPError」是誤報。
    import socket
    import threading
    import urllib.error

    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    held = []
    threading.Thread(target=lambda: held.append(srv.accept()), daemon=True).start()
    try:
        rn.post(f"http://127.0.0.1:{srv.getsockname()[1]}/hook", "x")
        kind = "沒有例外"
    except Exception as e:  # noqa: BLE001 — 要看的就是它丟了什麼
        kind = type(e).__name__
    srv.close()
    check("X4 讀取逾時丟 TimeoutError，post 沒接住", kind == "TimeoutError", kind)
    check("PB7 補充：HTTPError 是 URLError 的子類別", issubclass(urllib.error.HTTPError, urllib.error.URLError))

print("\n" + ("ALL AS EXPECTED" if not failures else f"{len(failures)} 格跟預期不符：{failures}"))
sys.exit(1 if failures else 0)
