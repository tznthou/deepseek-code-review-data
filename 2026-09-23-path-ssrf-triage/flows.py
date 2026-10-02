"""把 SARIF 裡 path-injection / full-ssrf 的每條 flow 攤平成「source → ... → sink」。

用法: python3 flows.py analysis-1823093375.sarif alerts.tsv
alerts.tsv: number<TAB>rule<TAB>path<TAB>line (open alert 清單, 用來對上 alert 編號)
"""

import json
import sys

RULES = {"py/path-injection", "py/full-ssrf"}


def loc(pl):
    p = pl["physicalLocation"]
    return p["artifactLocation"]["uri"], p["region"]["startLine"]


def main():
    sarif = json.load(open(sys.argv[1]))
    alerts = {}
    for row in open(sys.argv[2]):
        num, rule, path, line = row.rstrip("\n").split("\t")
        alerts[(rule, path, int(line))] = num

    for res in sarif["runs"][0]["results"]:
        if res["ruleId"] not in RULES:
            continue
        uri, line = loc(res["locations"][0])
        num = alerts.get((res["ruleId"], uri, line), "?")
        print(f"#{num} {res['ruleId']} {uri}:{line}")
        print(f"  msg: {res['message']['text']}")
        for rl in res.get("relatedLocations", []):
            ruri, rline = loc(rl)
            print(f"  source[{rl.get('id')}]: {ruri}:{rline}")
        for i, cf in enumerate(res.get("codeFlows", [])):
            for tf in cf["threadFlows"]:
                steps = []
                for step in tf["locations"]:
                    suri, sline = loc(step["location"])
                    short = suri.rsplit("/", 1)[-1]
                    note = step["location"].get("message", {}).get("text", "")
                    steps.append(f"{short}:{sline}({note})")
                print(f"  flow{i}: " + " → ".join(steps))
        print()


if __name__ == "__main__":
    main()
