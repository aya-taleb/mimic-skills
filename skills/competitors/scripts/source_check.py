#!/usr/bin/env python3
"""Check a research file before anyone acts on it. Standard library only, no network.

Finds facts that have no link and checks that the file says when it was checked.
It does not open links or judge whether a fact is true. It catches the easy misses:
a table row with no URL, a price in a bullet with no source, a missing check date.

    python3 source_check.py founder/competitors.md
    python3 source_check.py founder/funding.md --date-column deadline
    python3 source_check.py founder/competitors.md --today 2026-10-23 --max-age-days 30
    python3 source_check.py founder/competitors.md --json

Rules:
  1. The file has a line "Checked: YYYY-MM-DD" (also "Last checked:" or "As of:").
  2. Every table data row has an http(s) link, or says "not found" or "not listed".
  3. Outside summary-style sections and the "Scope:" line, a line with a money amount or a percent needs a link.
     Summary-style sections (they restate rows above) are skipped: Summary, The gap,
     For the next steps, Not found, and any heading passed with --derived.
  4. With --date-column NAME, each cell in that column is a date (YYYY-MM-DD), or one of:
     rolling, not listed, closed, tbd. Use it for deadlines.
  5. With --max-age-days, the check date must be no older than that.

Exit code 0 when clean, 1 when there are problems, 2 on bad input.
"""

import argparse
import datetime
import json
import re
import sys

CHECK_DATE = re.compile(r"(?im)^\s*\**\s*(?:last\s+checked|checked|as\s+of)\s*\**\s*:\s*\**\s*(\d{4}-\d{2}-\d{2})")
URL = re.compile(r"https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}\S*")
MONEY_OR_PCT = re.compile(r"(?:[$€£]\s?\d)|(?:\d\s?(?:USD|EUR|GBP)\b)|(?:\d+(?:\.\d+)?\s?%)")
EXEMPT_ROW = re.compile(r"(?i)\bnot (?:found|listed|public)\b")
DATE_CELL = re.compile(r"^\d{4}-\d{2}-\d{2}\b")
DATE_WORDS = ("rolling", "not listed", "closed", "tbd")
DEFAULT_DERIVED = ("summary", "the gap", "for the next steps", "not found", "next steps")
SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}")


def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def check(text, date_column=None, derived=(), today=None, max_age_days=None):
    """Return a list of problems: dicts with line, kind, text. Pure function."""
    problems = []
    derived_names = tuple(d.lower() for d in DEFAULT_DERIVED + tuple(derived))
    m = CHECK_DATE.search(text)
    check_date = None
    if not m:
        problems.append({"line": 0, "kind": "no-check-date",
                         "text": "add a line 'Checked: YYYY-MM-DD' near the top"})
    else:
        try:
            check_date = datetime.date.fromisoformat(m.group(1))
        except ValueError:
            problems.append({"line": 0, "kind": "bad-check-date", "text": m.group(1)})
    if check_date and max_age_days is not None:
        ref = today or datetime.date.today()
        age = (ref - check_date).days
        if age > max_age_days:
            problems.append({"line": 0, "kind": "stale",
                             "text": "checked %d days ago (limit %d); look again" % (age, max_age_days)})

    section = ""
    in_fence = False
    header = None
    date_idx = None
    saw_date_column = False
    for n, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("#"):
            section = stripped.lstrip("#").strip().lower()
            header = None
            continue
        in_derived = any(section.startswith(d) for d in derived_names)
        if re.match(r"(?i)^\**\s*scope\s*\**\s*:", stripped):
            continue  # the scope line restates the user's own plan
        if stripped.startswith("|"):
            if SEPARATOR.match(stripped):
                continue
            cells = split_row(stripped)
            if header is None:
                header = [c.lower() for c in cells]
                date_idx = header.index(date_column.lower()) if date_column and date_column.lower() in header else None
                saw_date_column = saw_date_column or date_idx is not None
                continue
            if in_derived:
                continue
            if not URL.search(stripped) and not EXEMPT_ROW.search(stripped):
                problems.append({"line": n, "kind": "row-without-link", "text": stripped[:120]})
            if date_idx is not None and date_idx < len(cells):
                cell = cells[date_idx].strip().lower()
                if not (DATE_CELL.match(cell) or any(cell.startswith(w) for w in DATE_WORDS)):
                    problems.append({"line": n, "kind": "undated", "text": "%s: %r" % (date_column, cells[date_idx])})
            continue
        header = None  # any non-table line ends the table
        if not stripped or in_derived:
            continue
        if MONEY_OR_PCT.search(stripped) and not URL.search(stripped) and not EXEMPT_ROW.search(stripped):
            if "{{" in stripped:
                continue  # a placeholder the user fills in
            problems.append({"line": n, "kind": "number-without-link", "text": stripped[:120]})
    if date_column and not saw_date_column:
        problems.append({"line": 0, "kind": "no-date-column", "text": "no table has a %r column" % date_column})
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description="Flag facts without links and missing check dates.")
    ap.add_argument("path")
    ap.add_argument("--date-column", help="table column whose cells must be dates, e.g. deadline")
    ap.add_argument("--derived", action="append", default=[], help="extra heading to skip (restates rows above)")
    ap.add_argument("--today", help="YYYY-MM-DD, default is today")
    ap.add_argument("--max-age-days", type=int)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        with open(a.path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print("cannot read %s: %s" % (a.path, exc), file=sys.stderr)
        return 2
    today = None
    if a.today:
        try:
            today = datetime.date.fromisoformat(a.today)
        except ValueError:
            print("--today must be YYYY-MM-DD", file=sys.stderr)
            return 2
    problems = check(text, a.date_column, a.derived, today, a.max_age_days)
    if a.json:
        print(json.dumps({"path": a.path, "problems": problems}, indent=2))
    elif problems:
        print("%s: %d problem(s)" % (a.path, len(problems)))
        for p in problems:
            where = "line %d" % p["line"] if p["line"] else "file"
            print("  %s  %s  %s" % (where, p["kind"], p["text"]))
    else:
        print("%s: clean (every fact has a link, check date present)" % a.path)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
