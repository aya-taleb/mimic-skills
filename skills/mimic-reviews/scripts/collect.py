#!/usr/bin/env python3
"""Turn saved review feeds and exports into mimic/reviews.csv. Standard library only.

This tool does not fetch anything. You (or Claude, with your yes) save the
official feed or the export to a file first, then this tool reads that file.
That keeps collection inside each source's terms and makes every run
repeatable.

    python3 collect.py apple-rss  saved/apple-p1.json saved/apple-p2.json --competitor "Acme"
    python3 collect.py hn-algolia saved/hn.json --competitor "Acme"
    python3 collect.py csv        export.csv --map "text=Review,rating=Stars,url=Link,date=Date"
    python3 collect.py paste      notes.txt --source g2 --competitor "Acme"
    python3 collect.py scrub      mimic/raw/*.json mimic/raw/*.csv

Every command appends to --out (default mimic/reviews.csv) and skips rows that
are already there. Columns written: source,url,date,rating,text,competitor,ref.
ref is the source's own id for the review when it has one (Apple has no link
per review, so its rows link the app's review feed and keep the id in ref).

What it keeps and drops:
  - A row needs a link (http or https) and text. Rows without one are dropped
    and counted. Nothing is guessed.
  - Reviewer names, emails, avatars and profile links are never written, even
    when the feed has them. The research is about what people said, not who.
  - Raw files you save yourself should not keep names either. `scrub` rewrites a
    saved JSON or CSV in place: it keeps url, date, rating and text and drops
    reviewer names, handles and profile links. apple-rss and hn-algolia do the
    same to the file they read when given --scrub. Never scrub a file the user
    gave you without asking: it is theirs.
  - Text is kept exactly, except that invisible characters (zero-width, bidi
    controls) and HTML tags from HN comments are removed.

Where the saved files come from:
  apple-rss   https://itunes.apple.com/<cc>/rss/customerreviews/page=<1-10>/id=<APP_ID>/sortby=mostrecent/json
              Apple's public feed. Up to 10 pages of 50 recent reviews per country.
  hn-algolia  https://hn.algolia.com/api/v1/search?query=<words>&tags=comment
              The public Hacker News search API.
  csv         any export you are allowed to use: your own Google Play Console or
              App Store Connect export (for your own app), a review site's CSV
              export, a sheet you filled by hand while reading pages.
  paste       review text you copied by hand from pages you read. Format below.

paste format: blocks separated by a blank line. Each block has a URL line,
optional "date: YYYY-MM-DD" and "rating: N" lines, then the text.

    https://www.g2.com/products/acme/reviews/acme-review-123
    date: 2026-05-02
    rating: 2
    The exact words of the review.
"""

import argparse
import csv
import html
import json
import os
import re
import sys

COLUMNS = ["source", "url", "date", "rating", "text", "competitor", "ref"]
INVISIBLE = re.compile("[​-‏‪-‮⁠-⁤﻿­]")
TAG = re.compile(r"<[^>]+>")
URL = re.compile(r"^https?://\S+$")


# Keys and columns that hold who wrote a review. Dropped from saved raw files.
PERSONAL_KEYS = {"author", "authors", "reviewer", "reviewer_name", "reviewername", "user",
                 "username", "user_name", "handle", "profile", "profile_url", "profileurl",
                 "avatar", "avatar_url", "email", "name", "nickname", "_highlightresult"}


class CollectError(Exception):
    pass


def _scrub_node(node):
    if isinstance(node, dict):
        return {k: _scrub_node(v) for k, v in node.items() if k.lower() not in PERSONAL_KEYS}
    if isinstance(node, list):
        return [_scrub_node(v) for v in node]
    return node


def scrub_file(path):
    """Rewrite a saved JSON or CSV without reviewer names. Return what was removed."""
    low = path.lower()
    if low.endswith(".json"):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        clean_data = _scrub_node(data)
        if clean_data == data:
            return "nothing to remove"
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(clean_data, fh, ensure_ascii=False, indent=1)
        return "author fields removed"
    if low.endswith(".csv"):
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            fields = reader.fieldnames or []
            keep = [f for f in fields if (f or "").strip().lower() not in PERSONAL_KEYS]
            rows = list(reader)
        if keep == fields:
            return "nothing to remove"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keep, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in keep})
        return "columns removed: %s" % ", ".join(f for f in fields if f not in keep)
    return "skipped: only .json and .csv can be scrubbed; check this file by hand"


def clean(text):
    return INVISIBLE.sub("", text or "").strip()


def _label(node):
    if isinstance(node, dict):
        return str(node.get("label", "")).strip()
    return str(node or "").strip()


def from_apple_rss(path, country="us"):
    """Rows from Apple's customer reviews RSS feed saved as JSON."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    feed = data.get("feed")
    if not isinstance(feed, dict):
        raise CollectError("%s is not an Apple customer reviews feed (no 'feed')" % path)
    entries = feed.get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]
    app_id = None
    rows = []
    for e in entries:
        if "im:rating" not in e:
            # The first entry on some pages is the app itself, not a review.
            m = re.search(r"id(\d+)", json.dumps(e.get("id", "")))
            app_id = app_id or (m.group(1) if m else None)
            continue
        review_id = _label(e.get("id"))
        title = _label(e.get("title"))
        body = _label(e.get("content"))
        text = clean(("%s. %s" % (title, body)) if title and body else (title or body))
        link = ""
        links = e.get("link")
        if isinstance(links, dict):
            link = links.get("attributes", {}).get("href", "")
        elif isinstance(links, list) and links:
            link = links[0].get("attributes", {}).get("href", "")
        rows.append({
            "source": "app-store-%s" % country,
            "url": link,
            "date": _label(e.get("updated"))[:10],
            "rating": _label(e.get("im:rating")),
            "text": text,
            # Apple has no public link per review. The url is the feed's own link
            # to the app's reviews; ref keeps the review id so it can be found.
            "ref": ("apple-review-%s" % review_id) if review_id else "",
        })
    return rows


def from_hn_algolia(path):
    """Rows from a saved hn.algolia.com search (comments or stories)."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    hits = data.get("hits")
    if not isinstance(hits, list):
        raise CollectError("%s is not an HN Algolia search result (no 'hits')" % path)
    rows = []
    for h in hits:
        raw = h.get("comment_text") or h.get("story_text") or h.get("title") or ""
        text = clean(html.unescape(TAG.sub(" ", raw)))
        text = re.sub(r"[ \t]+", " ", text)
        oid = str(h.get("objectID", "")).strip()
        rows.append({
            "source": "hacker-news",
            "url": ("https://news.ycombinator.com/item?id=%s" % oid) if oid else "",
            "date": str(h.get("created_at", ""))[:10],
            "rating": "",
            "text": text,
            "ref": ("hn-%s" % oid) if oid else "",
        })
    return rows


def parse_map(spec):
    """'text=Review Body,rating=Stars' -> {'text': 'Review Body', 'rating': 'Stars'}"""
    out = {}
    for part in (spec or "").split(","):
        if not part.strip():
            continue
        if "=" not in part:
            raise CollectError("--map entries look like ours=theirs, got %r" % part)
        ours, theirs = part.split("=", 1)
        ours = ours.strip().lower()
        if ours not in ("source", "url", "date", "rating", "text"):
            raise CollectError("--map: %r is not one of source,url,date,rating,text" % ours)
        out[ours] = theirs.strip()
    return out


def from_csv(path, mapping=None, source=""):
    mapping = mapping or {}
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise CollectError("%s is empty" % path)
        lower = {f.strip().lower(): f for f in reader.fieldnames if f}
        cols = {}
        for ours in ("source", "url", "date", "rating", "text"):
            theirs = mapping.get(ours, ours)
            cols[ours] = lower.get(theirs.strip().lower())
        if not cols["text"]:
            raise CollectError("%s: no text column. Use --map text=<their column name>" % path)
        for raw in reader:
            get = lambda k: (raw.get(cols[k]) or "").strip() if cols[k] else ""
            rows.append({
                "source": get("source") or source,
                "url": get("url"),
                "date": get("date")[:10],
                "rating": get("rating"),
                "text": clean(get("text")),
            })
    return rows


def from_paste(path, source=""):
    with open(path, encoding="utf-8") as fh:
        blocks = re.split(r"\n\s*\n", fh.read().strip())
    rows = []
    for b in blocks:
        lines = [l.rstrip() for l in b.strip().splitlines()]
        if not lines:
            continue
        url = lines[0].strip() if URL.match(lines[0].strip()) else ""
        rest = lines[1:] if url else lines
        date = rating = ""
        body = []
        for l in rest:
            m = re.match(r"^\s*(date|rating)\s*:\s*(.+)$", l, re.I)
            if m and not body:
                if m.group(1).lower() == "date":
                    date = m.group(2).strip()[:10]
                else:
                    rating = m.group(2).strip()
                continue
            body.append(l)
        rows.append({"source": source, "url": url, "date": date, "rating": rating,
                     "text": clean("\n".join(body))})
    return rows


def existing_keys(path):
    keys = set()
    if not os.path.isfile(path):
        return keys
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            keys.add(_key(row))
    return keys


def _key(row):
    return (row.get("url", "").strip(), re.sub(r"\W+", " ", row.get("text", "").lower()).strip())


def append(rows, out_path, competitor=""):
    """Append valid rows to out_path. Return (added, dropped, duplicates)."""
    seen = existing_keys(out_path)
    new_file = not os.path.isfile(out_path) or os.path.getsize(out_path) == 0
    folder = os.path.dirname(out_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    added = dropped = dupes = 0
    with open(out_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        if new_file:
            w.writeheader()
        for r in rows:
            r = dict(r)
            r["competitor"] = r.get("competitor") or competitor
            if not r.get("text") or not re.match(r"^https?://", r.get("url", "")):
                dropped += 1
                continue
            k = _key(r)
            if k in seen:
                dupes += 1
                continue
            seen.add(k)
            w.writerow({c: r.get(c, "") for c in COLUMNS})
            added += 1
    return added, dropped, dupes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("kind", choices=("apple-rss", "hn-algolia", "csv", "paste", "scrub"))
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default=os.path.join("mimic", "reviews.csv"))
    ap.add_argument("--competitor", default="", help="which competitor these are about")
    ap.add_argument("--source", default="", help="source name for csv and paste rows")
    ap.add_argument("--country", default="us", help="apple-rss: the store country")
    ap.add_argument("--map", default="", help="csv: ours=theirs column names")
    ap.add_argument("--scrub", action="store_true",
                    help="apple-rss, hn-algolia: also strip reviewer names from the saved file")
    args = ap.parse_args(argv)
    if args.kind == "scrub":
        try:
            for f in args.files:
                print("%s: %s" % (f, scrub_file(f)))
        except (OSError, ValueError, csv.Error) as exc:
            print("collect: %s" % exc, file=sys.stderr)
            return 2
        return 0
    total = [0, 0, 0]
    try:
        mapping = parse_map(args.map)
        for f in args.files:
            if args.kind == "apple-rss":
                rows = from_apple_rss(f, args.country)
            elif args.kind == "hn-algolia":
                rows = from_hn_algolia(f)
            elif args.kind == "csv":
                rows = from_csv(f, mapping, args.source)
            else:
                rows = from_paste(f, args.source)
            if args.kind in ("apple-rss", "hn-algolia") and args.scrub:
                print("%s: %s" % (f, scrub_file(f)))
            a, d, u = append(rows, args.out, args.competitor)
            total = [total[0] + a, total[1] + d, total[2] + u]
            print("%s: %d added, %d dropped (no link or no text), %d already there"
                  % (f, a, d, u))
    except (CollectError, OSError, ValueError, csv.Error) as exc:
        print("collect: %s" % exc, file=sys.stderr)
        return 2
    print("total: %d added to %s" % (total[0], args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
