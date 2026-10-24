import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(__file__))
from _load import load  # noqa: E402

listing = load("mimic-launch", "listing")
EXAMPLE = os.path.join(os.path.dirname(listing.__file__), "..", "references",
                       "listing.example.json")


def levels(issues, level):
    return [i for i in issues if i["level"] == level]


class ListingTest(unittest.TestCase):
    def setUp(self):
        with open(EXAMPLE, encoding="utf-8") as fh:
            self.example = json.load(fh)

    def test_example_is_clean(self):
        self.assertEqual(listing.lint(self.example), [])

    def test_avoid_name_is_an_error(self):
        data = dict(self.example)
        data["app_store"] = dict(data["app_store"], subtitle="Like Name Of The Competitor")
        errs = levels(listing.lint(data), "error")
        self.assertTrue(any("Name Of The Competitor" in e["message"] for e in errs))

    def test_app_store_name_limit(self):
        data = {"app_store": dict(self.example["app_store"], name="x" * 31)}
        errs = levels(listing.lint(data), "error")
        self.assertTrue(any(e["field"] == "name" and "31 characters" in e["message"] for e in errs))

    def test_google_business_link_and_promo(self):
        data = {"google_business": {"name": "Lunch Club | Best lunch near me",
                                    "description": "Fresh lunch. 20% off this week. www.lunch.com"}}
        issues = listing.lint(data)
        self.assertTrue(any(i["field"] == "description" and i["level"] == "error"
                            for i in issues))
        self.assertTrue(any("promotion" in i["message"] for i in issues))
        self.assertTrue(any(i["field"] == "name" for i in levels(issues, "warn")))

    def test_google_business_description_limit(self):
        data = {"google_business": {"name": "Lunch Club", "description": "a" * 751}}
        errs = levels(listing.lint(data), "error")
        self.assertTrue(any("751 characters, limit is 750" in e["message"] for e in errs))

    def test_proof_claims_found(self):
        for text in ("Trusted by 2,000+ teams", "Rated 4.9 stars", "As seen on TV",
                     "Join 10k happy customers", '"It changed my week completely" - Sarah'):
            self.assertTrue(listing.proof_claims(text), text)

    def test_plain_copy_has_no_proof_claims(self):
        for text in ("Book a lunch in two taps.", "Cancel any time from settings.",
                     "Three steps: pick, pay, eat."):
            self.assertEqual(listing.proof_claims(text), [], text)

    def test_proof_ok_allows_a_checked_claim(self):
        self.assertEqual(listing.proof_claims("212 people on the waitlist",
                                              ["212 people on the waitlist"]), [])

    def test_lint_copy_file(self):
        tmp = tempfile.mkdtemp()
        p = os.path.join(tmp, "landing.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# Hero\nBetter than Acme.\nTrusted by 500 teams.\n")
        issues = listing.lint_copy(p, ["Acme"])
        self.assertEqual(len(levels(issues, "error")), 1)
        self.assertEqual(len(levels(issues, "warn")), 1)
        self.assertEqual(issues[0]["field"], "line 2")

    def test_cli_exit_codes(self):
        tmp = tempfile.mkdtemp()
        bad = os.path.join(tmp, "l.json")
        with open(bad, "w", encoding="utf-8") as fh:
            json.dump({"avoid": ["Acme"], "google_play": {"title": "Acme killer",
                       "short_description": "x", "full_description": "y"}}, fh)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(listing.main([EXAMPLE]), 0)
            self.assertEqual(listing.main([bad]), 1)
            self.assertEqual(listing.main([os.path.join(tmp, "missing.json")]), 2)


if __name__ == "__main__":
    unittest.main()
