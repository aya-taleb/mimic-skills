#!/usr/bin/env python3
"""Bug log checker for mimic-test and the mimic-deploy gate. Standard library only.

Reads the bug table in mimic/test/bugs.md, checks every row is complete, counts
open bugs by severity, and says whether deploy is blocked.

    python3 bugs.py mimic/test/bugs.md
    python3 bugs.py mimic/test/bugs.md --json
    python3 bugs.py mimic/test/bugs.md --gate        # exit 1 if any S1 or S2 is open

The table (one header row, then one row per bug):

    | id | title | severity | status | flow | found | steps |
    | --- | --- | --- | --- | --- | --- | --- |
    | B001 | Second booking for a taken slot goes through | S1 | open | F01 | 2026-10-20 | 1. ... |

severity: S1 data loss, money, security, or the core loop broken
          S2 a must feature broken with no workaround
          S3 broken, but there is a workaround
          S4 cosmetic
status:   open, fixing, fixed, verified, wontfix
          "fixed" still counts as open for the gate until a test has run on it
          and it is marked verified. wontfix is not allowed for S1.
"""

import argparse
import json
import re
import sys

SEVERITIES = ("S1", "S2", "S3", "S4")
OPEN = ("open", "fixing", "fixed")
CLOSED = ("verified", "wontfix")
NEEDED = ("id", "title", "severity", "status")


class BugLogError(Exception):
    pass


def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def parse(text):
    """Return (rows, problems). Reads the first markdown table with an id column."""
    rows, problems = [], []
    header = None
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s.startswith("|"):
            if header is not None and rows:
                break
            continue
        cells = split_row(s)
        if header is None:
            low = [c.lower() for c in cells]
            if "id" in low and "severity" in low:
                header = low
            continue
        if set(s) <= set("|-: "):
            continue
        row = dict(zip(header, cells))
        row["_line"] = n
        rows.append(row)
    if header is None:
        raise BugLogError("no bug table found. It needs a header row with at least: "
                          "id, title, severity, status")
    missing = [c for c in NEEDED if c not in header]
    if missing:
        raise BugLogError("the bug table has no %s column" % ", ".join(missing))
    seen = set()
    for r in rows:
        where = "line %d (%s)" % (r["_line"], r.get("id") or "no id")
        for c in NEEDED:
            if not r.get(c):
                problems.append("%s: %s is empty" % (where, c))
        sev = r.get("severity", "").upper()
        if sev and sev not in SEVERITIES:
            problems.append("%s: severity %r is not S1, S2, S3 or S4" % (where, r["severity"]))
        st = r.get("status", "").lower()
        if st and st not in OPEN + CLOSED:
            problems.append("%s: status %r is not one of %s"
                            % (where, r["status"], ", ".join(OPEN + CLOSED)))
        if sev == "S1" and st == "wontfix":
            problems.append("%s: an S1 cannot be wontfix. Fix it, or lower the severity "
                            "with a reason if it was rated wrong" % where)
        if "steps" in r and not r.get("steps") and st in OPEN:
            problems.append("%s: no steps to reproduce" % where)
        if r.get("id"):
            if r["id"] in seen:
                problems.append("%s: duplicate id" % where)
            seen.add(r["id"])
    return rows, problems


def summary(rows, problems):
    counts = {s: {"open": 0, "closed": 0} for s in SEVERITIES}
    blockers = []
    for r in rows:
        sev = r.get("severity", "").upper()
        st = r.get("status", "").lower()
        if sev not in counts:
            continue
        if st in CLOSED:
            counts[sev]["closed"] += 1
        else:
            counts[sev]["open"] += 1
            if sev in ("S1", "S2"):
                blockers.append({"id": r.get("id", ""), "title": r.get("title", ""),
                                 "severity": sev, "status": st or "open"})
    return {"total": len(rows), "by_severity": counts, "blockers": blockers,
            "problems": problems, "deploy_blocked": bool(blockers or problems)}


def render(s):
    out = ["%d bugs logged" % s["total"]]
    for sev in SEVERITIES:
        c = s["by_severity"][sev]
        out.append("  %s  open %d  closed %d" % (sev, c["open"], c["closed"]))
    if s["problems"]:
        out.append("")
        out.append("Fix the log first:")
        out.extend("  - " + p for p in s["problems"])
    out.append("")
    if s["blockers"]:
        out.append("Deploy blocked by %d open S1/S2:" % len(s["blockers"]))
        for b in s["blockers"]:
            out.append("  - %s [%s, %s] %s" % (b["id"], b["severity"], b["status"], b["title"]))
    elif s["problems"]:
        out.append("Deploy blocked until the log is complete.")
    else:
        out.append("No open S1 or S2. The bug gate passes.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("log", help="mimic/test/bugs.md")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gate", action="store_true", help="exit 1 if deploy is blocked")
    args = ap.parse_args(argv)
    try:
        with open(args.log, encoding="utf-8") as fh:
            rows, problems = parse(fh.read())
    except (OSError, BugLogError) as exc:
        print("bugs: %s" % exc, file=sys.stderr)
        return 2
    s = summary(rows, problems)
    print(json.dumps(s, indent=2) if args.json else render(s))
    if args.gate and s["deploy_blocked"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
