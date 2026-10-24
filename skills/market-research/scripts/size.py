#!/usr/bin/env python3
"""Bottom-up market size from a small inputs file, with every number tied to its source.

Bottom-up means: how many buyers could buy, times how much each pays in a year, then the
share you could actually reach and win. Each input says where it came from. Inputs with
no source are allowed only as assumptions, and the output labels them that way, so a
guess never reads like a fact.

Input (JSON):
{
  "unit": "offices",                          what one buyer is
  "currency": "USD",
  "inputs": {
    "buyers":   {"value": 1840, "source": "https://...", "note": "offices with 20-199 staff, King County, CBP 2022"},
    "price":    {"value": 9,    "source": "founder", "note": "per person per lunch"},
    "per_year": {"value": 2800, "assumption": "20 people x 2 lunches x 70 weeks? check", "note": "..."},
    "reachable":{"value": 0.30, "assumption": "share inside the delivery zone"},
    "win":      {"value": 0.05, "assumption": "share of reachable we could win in 3 years"}
  },
  "formula": {
    "TAM": "buyers * per_year * price",
    "SAM": "TAM * reachable",
    "SOM": "SAM * win"
  },
  "top_down": [                               optional: published figures to compare against
    {"label": "US catering market 2024", "value": 6.7e10, "source": "https://..."}
  ]
}

Formulas use + - * / ( ) and the input names, or earlier results (TAM, SAM).
Values can be single numbers or [low, high] ranges; ranges flow through the math.

Usage:
  python3 size.py inputs.json                 # markdown table to stdout
  python3 size.py inputs.json --json
  python3 size.py inputs.json --out founder/market-sizing.md

Standard library only.
"""
import argparse
import ast
import json
import operator
import sys

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


class SizeError(Exception):
    pass


def as_range(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return (float(v), float(v))
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
        lo, hi = float(v[0]), float(v[1])
        if lo > hi:
            lo, hi = hi, lo
        return (lo, hi)
    raise SizeError("value must be a number or [low, high]: %r" % (v,))


def combine(op, a, b):
    if op is operator.truediv and (b[0] <= 0 <= b[1]):
        raise SizeError("division by a range that includes zero")
    vals = [op(x, y) for x in a for y in b]
    return (min(vals), max(vals))


def evaluate(expr, names):
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise SizeError("bad formula %r: %s" % (expr, exc))

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return combine(OPS[type(node.op)], walk(node.left), walk(node.right))
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise SizeError("formula uses %r, which is not an input or an earlier result" % node.id)
            return names[node.id]
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return (float(node.value), float(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            lo, hi = walk(node.operand)
            return (-hi, -lo)
        raise SizeError("only + - * / ( ), numbers and input names are allowed in %r" % expr)

    return walk(tree)


def deps(expr):
    return sorted({n.id for n in ast.walk(ast.parse(expr, mode="eval")) if isinstance(n, ast.Name)})


def compute(spec):
    inputs = spec.get("inputs") or {}
    if not inputs:
        raise SizeError("no inputs")
    names, rows = {}, []
    for key, item in inputs.items():
        if not isinstance(item, dict) or "value" not in item:
            raise SizeError("input %r needs a value" % key)
        src = (item.get("source") or "").strip()
        assumption = (item.get("assumption") or "").strip()
        if not src and not assumption:
            raise SizeError("input %r has no source and is not marked as an assumption. "
                            "Add \"source\" (a link or 'founder') or \"assumption\" (why you think so)." % key)
        names[key] = as_range(item["value"])
        rows.append({"name": key, "value": names[key], "source": src, "assumption": assumption,
                     "note": item.get("note", ""), "kind": "sourced" if src else "assumption"})
    results = []
    for label, expr in (spec.get("formula") or {}).items():
        val = evaluate(expr, names)
        names[label] = val
        used = deps(expr)
        # an output is only as good as its weakest input
        leaves = set()
        stack = list(used)
        while stack:
            n = stack.pop()
            if n in inputs:
                leaves.add(n)
            else:
                for r in results:
                    if r["name"] == n:
                        stack.extend(r["uses"])
        guessed = sorted(n for n in leaves if not (inputs[n].get("source") or "").strip())
        results.append({"name": label, "formula": expr, "value": val, "uses": used,
                        "assumptions_used": guessed})
    return {"unit": spec.get("unit", "buyers"), "currency": spec.get("currency", "USD"),
            "inputs": rows, "results": results, "top_down": spec.get("top_down") or []}


def money(x, cur="USD"):
    sign = "-" if x < 0 else ""
    x = abs(x)
    sym = {"USD": "$", "EUR": "€", "GBP": "£"}.get(cur, cur + " ")
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if x >= div:
            return "%s%s%.1f%s" % (sign, sym, x / div, suf)
    return "%s%s%.0f" % (sign, sym, x)


def num(x):
    if 0 < abs(x) < 1:
        return "%.0f%%" % (x * 100) if (x * 100) == int(x * 100) else "%.1f%%" % (x * 100)
    if x == int(x):
        return "{:,}".format(int(x))
    return "{:,.2f}".format(x)


def show(rng, fmt):
    lo, hi = rng
    return fmt(lo) if lo == hi else "%s to %s" % (fmt(lo), fmt(hi))


def to_markdown(res):
    cur = res["currency"]
    out = ["## Bottom-up sizing", "",
           "| input | value | where it comes from |", "| --- | --- | --- |"]
    for r in res["inputs"]:
        where = r["source"] if r["source"] else "ASSUMPTION: " + r["assumption"]
        if r["note"]:
            where += " (" + r["note"] + ")"
        out.append("| %s | %s | %s |" % (r["name"], show(r["value"], num), where.replace("|", "/")))
    out += ["", "| result | formula | value | rests on guesses |", "| --- | --- | --- | --- |"]
    for r in res["results"]:
        guess = ", ".join(r["assumptions_used"]) or "none, all sourced"
        out.append("| %s | `%s` | %s | %s |" % (r["name"], r["formula"], show(r["value"], lambda v: money(v, cur)), guess))
    if res["top_down"]:
        out += ["", "## Top-down check", "", "| figure | value | source |", "| --- | --- | --- |"]
        for t in res["top_down"]:
            v = t.get("value")
            vs = show(as_range(v), lambda x: money(x, cur)) if v is not None else "{{number}}"
            out.append("| %s | %s | %s |" % (t.get("label", ""), vs, t.get("source") or "{{source needed}}"))
    guessed = sorted({g for r in res["results"] for g in r["assumptions_used"]})
    out.append("")
    if guessed:
        out.append("Assumptions to test before trusting these numbers: %s." % ", ".join(guessed))
    else:
        out.append("Every input has a source.")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bottom-up market sizing with sources.")
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    try:
        with open(args.file, encoding="utf-8") as fh:
            spec = json.load(fh)
        res = compute(spec)
    except (OSError, ValueError, SizeError) as exc:
        print("size.py: %s" % exc, file=sys.stderr)
        return 1
    if args.json:
        text = json.dumps(res, indent=2)
    else:
        text = to_markdown(res)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
