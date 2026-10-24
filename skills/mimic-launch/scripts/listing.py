#!/usr/bin/env python3
"""Listing and launch copy linter for mimic-launch. Standard library only.

Based on listing.py from replica-launch by Jake Schincariol (MIT, see
CREDITS.md). Changed by Aya Taleb: a Google Business Profile section for local
businesses, and a proof check that flags testimonials, user counts, ratings
and press claims in any copy file, so nothing fake ships.

Checks an App Store, Google Play or Google Business Profile listing against
the field limits and the mistakes that get a copycat rejected: a competitor's
name in your metadata, ranking claims in the title, wasted keyword characters.

    python3 listing.py mimic/launch/listing.json
    python3 listing.py listing.json --avoid "Competitor One,Its Company"
    python3 listing.py listing.json --proof mimic/launch/landing.md
    python3 listing.py listing.json --json

listing.json (see listing.example.json):

    {
      "avoid": ["Competitor Name", "Its Company"],
      "proof_ok": ["a claim you can back up, with its source"],
      "app_store":   {"name", "subtitle", "promotional_text", "description",
                      "keywords", "whats_new"},
      "google_play": {"title", "short_description", "full_description"},
      "google_business": {"name", "description"}
    }

Leave out a listing you are not using. --proof checks any text or markdown
file (the landing page, an email) for the avoid names and for proof claims.
Exit code 1 on any error, 0 when there are only warnings.
"""

import argparse
import json
import os
import re
import sys
import unicodedata

LIMITS = {
    "app_store": {"name": 30, "subtitle": 30, "promotional_text": 170,
                  "description": 4000, "keywords": 100, "whats_new": 4000},
    "google_play": {"title": 30, "short_description": 80, "full_description": 4000},
    # Google Business Profile: description up to 750 characters, no links, no
    # promotions or prices (support.google.com/business/answer/3039617).
    # The name has no published limit; it must match the real-world signage.
    "google_business": {"name": 0, "description": 750},
}
URL_RX = re.compile(r"(https?://|www\.|\b[a-z0-9-]+\.(com|net|org|io|co|app)\b)", re.I)
PROMO_RX = re.compile(r"(\$\s?\d|\b\d+% off\b|\bsale\b|\bdiscount\b|\bcoupon\b|\bpromo\b|\bfree trial\b)", re.I)
# Proof that has to be real: testimonials, counts, ratings, press, logos.
PROOF_RX = re.compile(
    r"(\b(trusted|loved|used) by\b"
    r"|\b\d[\d,.]*\s*\+?\s*(k\b|m\b)?\s*(happy |satisfied )?(users|customers|clients|teams|companies|businesses|members|downloads|orders|subscribers)\b"
    r"|\b[1-5](\.\d)?\s*(/\s*5\s*)?(stars?|\u2605)"
    r"|\brated \d"
    r"|\bas (seen|featured) (in|on)\b"
    r"|\bfeatured in\b"
    r"|\baward.?winning\b"
    r"|\btestimonials?\b"
    r"|^\s*>\s*[\"\u201c].+[\"\u201d]\s*$"
    r"|[\"\u201c][^\"\u201d]{12,}[\"\u201d]\s*(\u2014|-|,)\s*[A-Z][a-z]+)", re.I | re.M)
SHORT_FIELDS = {"name", "subtitle", "title", "short_description"}
CLAIMS = re.compile(
    r"(#\s?1\b|\bnumber one\b|\bno\.? ?1\b|\bbest\b|\btop[- ]rated\b|\b(app|game) of the year\b"
    r"|\bfree\b|\bdiscount\b|\bsale\b|\b\d+% off\b|\bnew!?$)", re.I)
STOP = {"a", "an", "and", "app", "for", "the", "to", "of", "with", "your", "you", "in", "on", "&"}


def length(text):
    """Characters as a person counts them (an emoji built from parts is one)."""
    text = unicodedata.normalize("NFC", text or "")
    count = 0
    prev_joiner = False
    for ch in text:
        cat = unicodedata.category(ch)
        if ch == "‍":
            prev_joiner = True
            continue
        if cat in ("Mn", "Me") or ch in ("️", "︎") or 0x1F3FB <= ord(ch) <= 0x1F3FF:
            continue
        if prev_joiner:
            prev_joiner = False
            continue
        count += 1
    return count


def has_emoji(text):
    return any(unicodedata.category(ch) == "So" or ord(ch) >= 0x1F000 for ch in text or "")


def words(text):
    return [w for w in re.findall(r"[a-z0-9']+", (text or "").lower()) if w not in STOP]


def lint(listing, avoid=None):
    issues = []
    avoid = [a.strip() for a in (avoid or listing.get("avoid") or []) if a.strip()]

    def add(level, store, field, msg):
        issues.append({"level": level, "store": store, "field": field, "message": msg})

    found_store = False
    for store, limits in LIMITS.items():
        data = listing.get(store)
        if not data:
            continue
        found_store = True
        for field, limit in limits.items():
            value = data.get(field, "")
            n = length(value)
            if not value:
                level = "error" if field in ("name", "title", "description",
                                             "full_description") else "warn"
                add(level, store, field, "empty")
                continue
            if limit and n > limit:
                add("error", store, field, "%d characters, limit is %d (%d over)"
                    % (n, limit, n - limit))
            for name in avoid:
                if re.search(r"(?<!\w)%s(?!\w)" % re.escape(name), value, re.I):
                    add("error", store, field,
                        "mentions '%s'. Another app's name or trademark in your "
                        "metadata gets the listing rejected and invites a takedown. "
                        "Describe what yours does instead." % name)
            if field in SHORT_FIELDS:
                m = CLAIMS.search(value)
                if m:
                    add("warn", store, field,
                        "'%s' reads as a ranking or price claim. Google Play bans "
                        "these in the title and short description, and Apple "
                        "rejects claims you cannot back up." % m.group(0).strip())
                if has_emoji(value):
                    add("warn", store, field, "emoji in a short field. Play rejects "
                        "them in titles; App Store reviewers often do too.")
                caps = re.findall(r"\b[A-Z]{4,}\b", value)
                if caps:
                    add("warn", store, field, "all-caps word(s): %s" % ", ".join(caps))
        if store == "google_business":
            desc = data.get("description", "")
            if URL_RX.search(desc):
                add("error", store, "description", "has a link or web address. Google "
                    "does not allow links in the business description.")
            m = PROMO_RX.search(desc)
            if m:
                add("warn", store, "description", "'%s' reads as a promotion or price. "
                    "Google asks for details about the business, not offers. Use a "
                    "Google post for offers." % m.group(0).strip())
            name = data.get("name", "")
            if re.search(r"(\||\s-\s|:|\bbest\b|\bnear me\b)", name, re.I):
                add("warn", store, "name", "looks like it has a tagline or keywords. "
                    "Google wants the name exactly as it appears on your sign.")
        if store == "app_store" and data.get("keywords"):
            kw_raw = data["keywords"]
            parts = [k.strip().lower() for k in kw_raw.split(",")]
            if re.search(r",\s", kw_raw):
                add("warn", store, "keywords", "spaces after commas waste characters. "
                    "Use word1,word2,word3")
            dupes = sorted({k for k in parts if k and parts.count(k) > 1})
            if dupes:
                add("warn", store, "keywords", "repeated: %s" % ", ".join(dupes))
            in_name = set(words(data.get("name", "")) + words(data.get("subtitle", "")))
            wasted = sorted({w for k in parts for w in words(k) if w in in_name})
            if wasted:
                add("warn", store, "keywords", "already in the name or subtitle, so "
                    "these characters are wasted: %s" % ", ".join(wasted))
            if any(not k for k in parts):
                add("warn", store, "keywords", "empty entry (double comma or trailing comma)")
    if not found_store:
        add("error", "-", "-", "no app_store, google_play or google_business section found")
    for store in LIMITS:
        for field, value in (listing.get(store) or {}).items():
            if isinstance(value, str):
                for claim in proof_claims(value, listing.get("proof_ok")):
                    add("warn", store, field, "proof claim '%s'. Keep it only if it is "
                        "real, you can show the source, and you have permission. Add it "
                        "to proof_ok once checked." % claim)
    return issues


def proof_claims(text, allowed=None):
    """Phrases that state proof (counts, ratings, testimonials, press)."""
    allowed = [a.lower() for a in (allowed or [])]
    found = []
    for m in PROOF_RX.finditer(text or ""):
        claim = m.group(0).strip()
        if any(claim.lower() in a or a in claim.lower() for a in allowed if a):
            continue
        found.append(claim[:80])
    return found


def lint_copy(path, avoid, allowed=None):
    """Check a copy file (landing page, email) for competitor names and proof."""
    issues = []
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for n, line in enumerate(lines, 1):
        for name in avoid:
            if re.search(r"(?<!\w)%s(?!\w)" % re.escape(name), line, re.I):
                issues.append({"level": "error", "store": os.path.basename(path),
                               "field": "line %d" % n,
                               "message": "mentions '%s'. Keep competitors' names out of "
                                          "your launch copy unless a lawyer has cleared a "
                                          "comparison." % name})
        claims = proof_claims(line, allowed)
        if claims:
            issues.append({"level": "warn", "store": os.path.basename(path),
                           "field": "line %d" % n,
                           "message": "proof claim '%s'. Real, sourced and with "
                                      "permission, or cut it." % "', '".join(claims)})
    return issues


def render(listing, issues):
    out = []
    for store, limits in LIMITS.items():
        data = listing.get(store)
        if not data:
            continue
        out.append(store.replace("_", " ").title())
        for field, limit in limits.items():
            n = length(data.get(field, ""))
            mark = "OVER" if limit and n > limit else ("ok" if n else "--")
            out.append("  %-18s %5d / %-5s %s" % (field, n, limit or "-", mark))
        out.append("")
    if not issues:
        out.append("No issues.")
    for i in issues:
        out.append("%-5s %s.%s: %s" % (i["level"].upper(), i["store"], i["field"],
                                       i["message"]))
    errs = sum(1 for i in issues if i["level"] == "error")
    warns = len(issues) - errs
    out.append("")
    out.append("%d errors, %d warnings" % (errs, warns))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("listing", help="listing.json")
    ap.add_argument("--avoid", help="comma-separated names that must not appear "
                                    "(the original app, its company)")
    ap.add_argument("--proof", nargs="*", default=[],
                    help="copy files to check for competitor names and proof claims")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        with open(args.listing, encoding="utf-8") as fh:
            listing = json.load(fh)
    except (OSError, ValueError) as exc:
        print("listing: %s" % exc, file=sys.stderr)
        return 2
    avoid = args.avoid.split(",") if args.avoid else None
    issues = lint(listing, avoid)
    names = [a.strip() for a in (avoid or listing.get("avoid") or []) if a.strip()]
    for path in args.proof:
        try:
            issues += lint_copy(path, names, listing.get("proof_ok"))
        except OSError as exc:
            print("listing: %s" % exc, file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        print(render(listing, issues))
    return 1 if any(i["level"] == "error" for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
