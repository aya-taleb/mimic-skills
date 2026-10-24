#!/usr/bin/env python3
"""Feedback ranker for mimic-reviews. Standard library only.

Based on reviews.py from replica-entrepreneur by Jake Schincariol (MIT, see
CREDITS.md). Changed by Aya Taleb: a competitor column, flags for text that
reads like instructions, invisible characters removed, and a pain-points.csv
that lead-gen can read.

Takes the real reviews you collected about the competitors and ranks what
their customers hate and what they keep asking for, with the exact words and
a link for every claim.

    python3 reviews.py mimic/reviews.csv
    python3 reviews.py mimic/reviews.csv --out mimic/feedback.md --pain-out mimic/pain-points.csv
    python3 reviews.py mimic/reviews.csv --json
    python3 reviews.py mimic/reviews.csv --themes themes-local.json

The CSV needs these columns (extra columns are ignored):

    source      where it came from: app-store, google-play, g2, capterra,
                trustpilot, google-maps, yelp, reddit, hacker-news, ...
    url         the link to the review or thread. Required.
    date        YYYY-MM-DD if you have it (YYYY-MM is fine)
    rating      1 to 5 stars if the source has stars, else blank
    text        the review, copied exactly. Required.
    competitor  which competitor it is about. Optional.

Reviewer names are never read or written, even if your CSV has them.
Review text is data. Rows whose text reads like instructions to an AI are
counted as normal reviews but listed under "Text that reads like
instructions", so a person can look at them. The tool never acts on them.

A row without a url or without text is dropped and counted, never guessed.
This tool only reorganises what you give it. It does not write reviews, it
does not paraphrase them, and every quote it prints is a substring of a row
you supplied, with that row's link.

How a theme is ranked: every review that matches it adds a weight. A 1 star
review adds 1.0, a 5 star review adds 0.2, an unrated one adds 0.6. Reviews
older than --months (default 18) count half.

What counts toward a complaint theme: rows rated 3 stars or less, unrated rows,
and 4 star rows with a "but" (but, however, wish, except, only problem...). A
5 star row, or a 4 star row with no "but", is praise: it is counted apart as
praise_matches and never adds to a complaint. Request themes count every row.

Labels: a theme with fewer than 3 reviews is "thin" (few reviews). A theme whose
reviews all come from one source is "one source", a separate flag: 54 App Store
reviews are not thin, but they are one source.

Curly quotes and apostrophes (common in iPhone text) are matched as straight
ones, so "doesn\u2019t" matches a doesn'?t pattern. Quotes keep the original text.
"""

import argparse
import csv
import datetime as _dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_THEMES = os.path.join(HERE, "themes.json")
SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
# Zero-width and direction characters hide text from people but not from models.
INVISIBLE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff\u00ad]")
# Curly to straight, one character for one, so positions in the text stay the same.
QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
                        "\u2032": "'", "\u201c": '"', "\u201d": '"', "\u201e": '"'})
# "Love it, but..." markers. A 4 star review with one of these is a complaint too.
CONTRAST = re.compile(r"\b(but|however|though|although|except|wish|if only|only (problem|issue|thing)"
                      r"|downside|con:|cons:|dislike)\b", re.I)
INSTRUCTION_LIKE = re.compile(
    r"(ignore (all |any )?(the |your )?(previous|prior|above) (instructions|rules)"
    r"|disregard (the|your|all) (instructions|rules)"
    r"|\b(system|developer) prompt\b"
    r"|\byou are (now )?(an? )?(ai|assistant|chatgpt|claude|language model)\b"
    r"|\b(as an|dear) (ai|assistant|llm|language model)\b"
    r"|\bnew instructions?:"
    r"|\b(rate|score|rank) (this|us|it) (as )?(5|five|10|the best)\b.{0,40}\b(ai|assistant|model)\b"
    r"|<\s*/?\s*(system|instructions?|prompt)\s*>)", re.I)


class FeedbackError(Exception):
    pass


def load_themes(path=DEFAULT_THEMES):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    themes = []
    for t in data.get("themes", []):
        themes.append({
            "id": t["id"], "label": t.get("label", t["id"]),
            "kind": t.get("kind", "complaint"),
            "patterns": [re.compile(p, re.I) for p in t.get("patterns", [])],
        })
    requests = [re.compile(p, re.I) for p in data.get("request_patterns", [])]
    return themes, requests


def parse_date(text):
    text = (text or "").strip()
    for fmt, n in (("%Y-%m-%d", 10), ("%Y-%m", 7)):
        try:
            return _dt.datetime.strptime(text[:n], fmt).date()
        except ValueError:
            continue
    return None


def parse_rating(text):
    text = (text or "").strip()
    if not text:
        return None
    m = re.match(r"^\s*(\d+(?:\.\d+)?)", text)
    if not m:
        return None
    value = float(m.group(1))
    if value < 1 or value > 5:
        return None
    return value


def load_reviews(path):
    """Return (kept rows, dropped count, duplicate count)."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise FeedbackError("%s is empty" % path)
        cols = [c.strip().lower() for c in reader.fieldnames]
        for need in ("url", "text"):
            if need not in cols:
                raise FeedbackError(
                    "%s has no '%s' column. Every review needs the link it came "
                    "from and its exact text: source,url,date,rating,text" % (path, need))
        kept, dropped, dupes = [], 0, 0
        seen = set()
        for i, raw in enumerate(reader, start=2):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
            url = row.get("url", "")
            text = INVISIBLE.sub("", row.get("text", "")).strip()
            if not url or not text or not re.match(r"^https?://", url):
                dropped += 1
                continue
            key = re.sub(r"\W+", " ", text.lower()).strip()
            if key in seen:
                dupes += 1
                continue
            seen.add(key)
            kept.append({
                "line": i,
                "source": row.get("source", "") or _host(url),
                "url": url,
                "date": parse_date(row.get("date", "")),
                "rating": parse_rating(row.get("rating", "")),
                "text": text,
                "competitor": row.get("competitor", ""),
                "ref": row.get("ref", ""),
                "instruction_like": bool(INSTRUCTION_LIKE.search(text)),
            })
    return kept, dropped, dupes


def _host(url):
    m = re.match(r"^https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else "unknown"


def weight(review, today, months):
    r = review["rating"]
    w = 0.6 if r is None else (6.0 - r) / 5.0
    if review["date"] is not None and today is not None:
        age_days = (today - review["date"]).days
        if age_days > months * 30.4:
            w *= 0.5
    return w


def norm(text):
    """Text for matching: curly quotes made straight, same length as the input."""
    return (text or "").translate(QUOTES)


def counts_as_complaint(review):
    """Low ratings, unrated rows, and 4 star rows with a 'but'. Never 5 stars."""
    r = review["rating"]
    if r is None or r <= 3:
        return True
    if r < 5 and CONTRAST.search(norm(review["text"])):
        return True
    return False


def snippet(text, pattern, limit=220):
    """The first sentence of text that matches pattern, verbatim (curly quotes kept)."""
    for sent in SENTENCE.split(text):
        if pattern.search(norm(sent)):
            s = sent.strip()
            if len(s) > limit:
                m = pattern.search(norm(s))
                start = max(0, m.start() - limit // 2)
                s = s[start:start + limit].strip()
                s = ("..." if start > 0 else "") + s + "..."
            return s
    s = text.strip()
    return s if len(s) <= limit else s[:limit].rstrip() + "..."


def analyse(reviews, themes, request_patterns, today=None, months=18):
    if today is None:
        today = _dt.date.today()
    results = {t["id"]: {"id": t["id"], "label": t["label"], "kind": t["kind"],
                         "reviews": [], "score": 0.0, "praise": 0} for t in themes}
    requests = []
    unthemed_negative = []
    flagged = [r for r in reviews if r.get("instruction_like")]
    for rv in reviews:
        w = weight(rv, today, months)
        matched = False
        text = norm(rv["text"])
        complaint_ok = counts_as_complaint(rv)
        for t in themes:
            hit = next((p for p in t["patterns"] if p.search(text)), None)
            if hit is None:
                continue
            matched = True
            res = results[t["id"]]
            if t["kind"] == "complaint" and not complaint_ok:
                res["praise"] += 1
                continue
            res["score"] += w
            res["reviews"].append({"rv": rv, "quote": snippet(rv["text"], hit)})
        req = next((p for p in request_patterns if p.search(text)), None)
        if req is not None and not rv.get("instruction_like"):
            requests.append({"quote": snippet(rv["text"], req), "url": rv["url"],
                             "source": rv["source"], "rating": rv["rating"],
                             "ref": rv.get("ref", "")})
        if (not matched and rv["rating"] is not None and rv["rating"] <= 2
                and not rv.get("instruction_like")):
            unthemed_negative.append(rv)

    total = len(reviews) or 1
    ranked = []
    for res in results.values():
        items = res["reviews"]
        if not items:
            continue
        rated = [x["rv"]["rating"] for x in items if x["rv"]["rating"] is not None]
        sources = sorted({x["rv"]["source"] for x in items})
        competitors = sorted({x["rv"].get("competitor", "") for x in items} - {""})
        # Lowest rated first, then shortest, so the quotes shown are the sharpest.
        items.sort(key=lambda x: (x["rv"]["rating"] if x["rv"]["rating"] is not None else 3,
                                  len(x["quote"])))
        ranked.append({
            "id": res["id"], "label": res["label"], "kind": res["kind"],
            "score": round(res["score"], 2),
            "count": len(items),
            "share_pct": round(100.0 * len(items) / total, 1),
            "avg_rating": round(sum(rated) / len(rated), 2) if rated else None,
            "sources": sources,
            "competitors": competitors,
            "thin": len(items) < 3,
            "one_source": len(sources) < 2,
            "praise_matches": res["praise"],
            "quotes": [{"quote": x["quote"], "url": x["rv"]["url"],
                        "source": x["rv"]["source"], "rating": x["rv"]["rating"],
                        "competitor": x["rv"].get("competitor", ""),
                        "ref": x["rv"].get("ref", "")}
                       for x in items if not x["rv"].get("instruction_like")][:3],
        })
    ranked.sort(key=lambda d: (-d["score"], -d["count"], d["id"]))
    return {
        "reviews": len(reviews),
        "sources": sorted({r["source"] for r in reviews}),
        "competitors": sorted({r.get("competitor", "") for r in reviews} - {""}),
        "per_competitor": {c: sum(1 for r in reviews if r.get("competitor", "") == c)
                           for c in sorted({r.get("competitor", "") for r in reviews} - {""})},
        "rated": sum(1 for r in reviews if r["rating"] is not None),
        "instruction_like": [{"url": r["url"], "source": r["source"], "ref": r.get("ref", ""),
                              "text": r["text"][:220]} for r in flagged],
        "themes": ranked,
        "requests": requests,
        "unthemed_negative": [{"url": r["url"], "source": r["source"], "ref": r.get("ref", ""),
                               "rating": r["rating"], "text": r["text"][:220]}
                              for r in unthemed_negative],
    }


def _stars(r):
    return "-" if r is None else ("%g*" % r)


def _link(item):
    """The url, plus the source's review id when the url is shared (Apple's feed)."""
    return item["url"] + ((" (%s)" % item["ref"]) if item.get("ref") else "")


def render(result, dropped=0, dupes=0):
    out = ["# What competitors' customers hate and want", ""]
    out.append("%d reviews from %d sources (%s). %d had star ratings." % (
        result["reviews"], len(result["sources"]), ", ".join(result["sources"]) or "none",
        result["rated"]))
    if result.get("per_competitor"):
        out.append("By competitor: %s." % ", ".join(
            "%s %d" % kv for kv in result["per_competitor"].items()))
    if dropped:
        out.append("%d rows dropped: no link or no text. Nothing is counted without "
                   "its source." % dropped)
    if dupes:
        out.append("%d duplicate reviews removed." % dupes)
    if result["reviews"] < 30:
        out.append("")
        out.append("Small sample. Under 30 reviews supports a direction, not a "
                   "ranking. Collect more before you bet the roadmap on it.")
    for kind, title in (("complaint", "What they hate"), ("request", "What they ask for")):
        rows = [t for t in result["themes"] if t["kind"] == kind]
        out.append("")
        out.append("## %s" % title)
        out.append("")
        if not rows:
            out.append("Nothing matched. Read the reviews by hand.")
            continue
        out.append("| rank | theme | score | reviews | share | avg stars | sources | competitors |")
        out.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for i, t in enumerate(rows, 1):
            flags = [f for f, on in (("thin", t["thin"]), ("one source", t.get("one_source"))) if on]
            out.append("| %d | %s%s | %.1f | %d | %.0f%% | %s | %d | %s |" % (
                i, t["label"], (" (%s)" % ", ".join(flags)) if flags else "", t["score"], t["count"],
                t["share_pct"], "-" if t["avg_rating"] is None else "%.1f" % t["avg_rating"],
                len(t["sources"]), ", ".join(t.get("competitors", [])) or "-"))
        if kind == "complaint":
            out.append("")
            out.append("Counted: rows rated 3 stars or less, unrated rows, and 4 star rows "
                       "with a \"but\". thin = under 3 reviews. one source = all from one "
                       "source: a direction, not a trend.")
            praised = [t for t in rows if t.get("praise_matches")]
            if praised:
                out.append("Praise left out (5 stars, or 4 with no \"but\"): %s." % ", ".join(
                    "%s %d" % (t["label"], t["praise_matches"]) for t in praised))
        for t in rows[:6]:
            out.append("")
            out.append("**%s**" % t["label"])
            for q in t["quotes"]:
                who = (q.get("competitor") + ", ") if q.get("competitor") else ""
                out.append('- "%s" (%s%s, %s) %s' % (q["quote"], who, q["source"],
                                                     _stars(q["rating"]), _link(q)))
    if result["requests"]:
        out.append("")
        out.append("## Asked for in their own words")
        out.append("")
        for q in result["requests"][:25]:
            out.append('- "%s" (%s, %s) %s' % (q["quote"], q["source"],
                                               _stars(q["rating"]), _link(q)))
    if result.get("instruction_like"):
        out.append("")
        out.append("## Text that reads like instructions")
        out.append("")
        out.append("These rows contain text aimed at an AI, not a review. They are data. "
                   "Nothing in them was followed, and none is quoted above. Check them "
                   "by hand and delete any that are not real reviews.")
        out.append("")
        for r in result["instruction_like"][:15]:
            out.append('- (%s) %s: "%s"' % (r["source"], _link(r), r["text"]))
    if result["unthemed_negative"]:
        out.append("")
        out.append("## Read these by hand")
        out.append("")
        out.append("Low ratings that matched no theme. Either noise, or a theme "
                   "themes.json does not have yet. Often the most useful part.")
        out.append("")
        for r in result["unthemed_negative"][:15]:
            out.append('- (%s, %s) %s: "%s"' % (r["source"], _stars(r["rating"]),
                                               _link(r), r["text"]))
    return "\n".join(out) + "\n"


PAIN_COLUMNS = ["rank", "theme", "kind", "label", "reviews", "share_pct", "avg_rating",
                "sources", "competitors", "thin", "quote", "quote_url", "quote_ref", "one_source"]


def write_pain_points(result, path):
    """pain-points.csv for lead-gen and other skills. No reviewer names, ever."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(PAIN_COLUMNS)
        for i, t in enumerate(result["themes"], 1):
            q = t["quotes"][0] if t["quotes"] else {"quote": "", "url": "", "ref": ""}
            w.writerow([i, t["id"], t["kind"], t["label"], t["count"], t["share_pct"],
                        "" if t["avg_rating"] is None else t["avg_rating"],
                        ";".join(t["sources"]), ";".join(t.get("competitors", [])),
                        "yes" if t["thin"] else "no", q["quote"], q["url"], q.get("ref", ""),
                        "yes" if t.get("one_source") else "no"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("reviews", help="CSV with source,url,date,rating,text")
    ap.add_argument("--themes", default=DEFAULT_THEMES)
    ap.add_argument("--months", type=int, default=18,
                    help="reviews older than this count half (default 18)")
    ap.add_argument("--today", help="YYYY-MM-DD, for reproducible runs")
    ap.add_argument("--out", help="write the markdown report here")
    ap.add_argument("--pain-out", help="write pain-points.csv here (for lead-gen)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        themes, req = load_themes(args.themes)
        reviews, dropped, dupes = load_reviews(args.reviews)
    except (FeedbackError, OSError, ValueError, KeyError, re.error) as exc:
        print("reviews: %s" % exc, file=sys.stderr)
        return 2
    if not reviews:
        print("reviews: no usable rows. Every row needs a url (http...) and the "
              "review text.", file=sys.stderr)
        return 2
    today = parse_date(args.today) if args.today else None
    result = analyse(reviews, themes, req, today=today, months=args.months)
    result["dropped"] = dropped
    result["duplicates"] = dupes
    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0
    text = render(result, dropped, dupes)
    if args.pain_out:
        write_pain_points(result, args.pain_out)
        print("wrote %s" % args.pain_out)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
