#!/usr/bin/env python3
"""Lock pass/fail lines for demand tests BEFORE they run, then read results against them.

The plan file (founder/validate-plan.json) holds 1 to 3 tests:

{
  "assumption": "Office managers will pre-pay for a second lunch route",
  "tests": [
    {
      "name": "pre-order page",
      "type": "pre-order",                  fake-door | waitlist | pre-order | concierge | other
      "metric": "pre-orders",               what you count
      "denominator": "unique visitors",     what you divide by (optional, for a rate)
      "pass_at": 0.05,                      at or above this is a pass
      "fail_below": 0.02,                   below this is a fail; between is "unclear"
      "min_sample": 200,                    don't call it before this many in the denominator
      "ends": "2026-11-15",
      "budget": 50
    }
  ]
}

Usage:
  python3 testplan.py lock founder/validate-plan.json
      checks the plan and writes a fingerprint and a lock date into it. After this,
      any change to a pass or fail line shows up in `read`.
  python3 testplan.py read founder/validate-plan.json results.json
      results.json: {"pre-order page": {"count": 14, "denominator": 260}}
      prints pass / fail / unclear / too early for each test and an overall read.

Standard library only.
"""
import argparse
import datetime
import hashlib
import json
import sys

TYPES = ("fake-door", "waitlist", "pre-order", "concierge", "other")
LOCKED_KEYS = ("name", "metric", "denominator", "pass_at", "fail_below", "min_sample")


class PlanError(Exception):
    pass


def fingerprint(test):
    core = {k: test.get(k) for k in LOCKED_KEYS}
    return hashlib.sha256(json.dumps(core, sort_keys=True).encode("utf-8")).hexdigest()[:12]


def check_plan(plan):
    problems = []
    if not (plan.get("assumption") or "").strip():
        problems.append("name the riskiest assumption in one line ('assumption')")
    tests = plan.get("tests") or []
    if not 1 <= len(tests) <= 3:
        problems.append("use 1 to 3 tests (found %d). More tests means none gets done well." % len(tests))
    names = set()
    for i, t in enumerate(tests, 1):
        label = t.get("name") or "test %d" % i
        if not t.get("name"):
            problems.append("%s: give it a name" % label)
        elif t["name"] in names:
            problems.append("%s: two tests share this name" % label)
        names.add(t.get("name"))
        if t.get("type") not in TYPES:
            problems.append("%s: type should be one of %s" % (label, ", ".join(TYPES)))
        if not t.get("metric"):
            problems.append("%s: say what you count ('metric')" % label)
        pa, fb = t.get("pass_at"), t.get("fail_below")
        if not isinstance(pa, (int, float)) or not isinstance(fb, (int, float)):
            problems.append("%s: set both 'pass_at' and 'fail_below' as numbers before the test runs" % label)
        elif fb > pa:
            problems.append("%s: fail_below (%s) is higher than pass_at (%s)" % (label, fb, pa))
        if t.get("denominator") and isinstance(pa, (int, float)) and pa > 1:
            problems.append("%s: with a denominator, pass_at is a rate between 0 and 1 (e.g. 0.05 for 5%%)" % label)
        if t.get("denominator") and not isinstance(t.get("min_sample"), (int, float)):
            problems.append("%s: set 'min_sample' so you don't call it on 12 visitors" % label)
        if not t.get("ends"):
            problems.append("%s: set an end date ('ends')" % label)
        else:
            try:
                datetime.date.fromisoformat(t["ends"])
            except ValueError:
                problems.append("%s: 'ends' should be YYYY-MM-DD" % label)
    return problems


def lock(plan, today=None):
    problems = check_plan(plan)
    if problems:
        raise PlanError("\n".join("- " + p for p in problems))
    stamp = today or datetime.date.today().isoformat()
    for t in plan["tests"]:
        t["locked_on"] = t.get("locked_on") or stamp
        t["fingerprint"] = fingerprint(t)
    return plan


def judge(test, result):
    count = result.get("count")
    if not isinstance(count, (int, float)):
        return "no data", "no count reported"
    denom = result.get("denominator")
    if test.get("denominator"):
        if not isinstance(denom, (int, float)) or denom <= 0:
            return "no data", "no %s reported" % test["denominator"]
        value = count / float(denom)
        shown = "%.1f%% (%s of %s %s)" % (value * 100, fmt(count), fmt(denom), test["denominator"])
        if denom < (test.get("min_sample") or 0):
            return "too early", "%s, under the %s %s you set" % (shown, fmt(test["min_sample"]), test["denominator"])
        pa, fb = "%.1f%%" % (test["pass_at"] * 100), "%.1f%%" % (test["fail_below"] * 100)
    else:
        value = float(count)
        shown = "%s %s" % (fmt(count), test["metric"])
        pa, fb = fmt(test["pass_at"]), fmt(test["fail_below"])
    if value >= test["pass_at"]:
        return "pass", "%s, at or above the pass line of %s" % (shown, pa)
    if value < test["fail_below"]:
        return "fail", "%s, below the fail line of %s" % (shown, fb)
    return "unclear", "%s, between the fail line %s and the pass line %s" % (shown, fb, pa)


def fmt(x):
    return str(int(x)) if float(x) == int(x) else "%.2f" % x


def read(plan, results):
    out = []
    for t in plan.get("tests", []):
        moved = bool(t.get("fingerprint")) and t["fingerprint"] != fingerprint(t)
        verdict, why = judge(t, results.get(t.get("name"), {}))
        out.append({"name": t.get("name"), "verdict": verdict, "why": why,
                    "locked": bool(t.get("fingerprint")), "lines_moved": moved})
    verdicts = [o["verdict"] for o in out]
    if any(o["lines_moved"] for o in out):
        overall = "The pass or fail lines changed after the plan was locked. Read results against the original lines."
    elif not all(o["locked"] for o in out):
        overall = "This plan was never locked, so there's no proof the lines were set before the test. Treat the read as soft."
    elif "too early" in verdicts or "no data" in verdicts:
        overall = "Not every test has enough data yet. Wait for the end date or the minimum sample."
    elif all(v == "pass" for v in verdicts):
        overall = "Every test passed its line. Evidence points to go."
    elif all(v == "fail" for v in verdicts):
        overall = "Every test failed its line. Evidence points to stop or a real pivot."
    else:
        overall = "Mixed results. Look at which assumption each test covered before calling go, pivot or stop."
    return {"tests": out, "overall": overall}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lock and read demand-test plans.")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("lock"); p.add_argument("plan")
    p = sub.add_parser("check"); p.add_argument("plan")
    p = sub.add_parser("read"); p.add_argument("plan"); p.add_argument("results"); p.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 1
    try:
        with open(args.plan, encoding="utf-8") as fh:
            plan = json.load(fh)
    except (OSError, ValueError) as exc:
        print("Could not read the plan: %s" % exc, file=sys.stderr)
        return 1
    if args.cmd == "check":
        problems = check_plan(plan)
        print("Plan looks ready to lock." if not problems else "Fix these first:\n" + "\n".join("- " + p for p in problems))
        return 0 if not problems else 2
    if args.cmd == "lock":
        try:
            lock(plan)
        except PlanError as exc:
            print("Not locked. Fix these first:\n%s" % exc, file=sys.stderr)
            return 2
        with open(args.plan, "w", encoding="utf-8") as fh:
            json.dump(plan, fh, indent=2)
            fh.write("\n")
        for t in plan["tests"]:
            print("Locked '%s' on %s (fingerprint %s)" % (t["name"], t["locked_on"], t["fingerprint"]))
        return 0
    try:
        with open(args.results, encoding="utf-8") as fh:
            results = json.load(fh)
    except (OSError, ValueError) as exc:
        print("Could not read the results: %s" % exc, file=sys.stderr)
        return 1
    res = read(plan, results)
    if args.json:
        print(json.dumps(res, indent=2))
        return 0
    for o in res["tests"]:
        flag = " (LINES CHANGED AFTER LOCK)" if o["lines_moved"] else ""
        print("- %s: %s. %s%s" % (o["name"], o["verdict"].upper(), o["why"], flag))
    print(res["overall"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
