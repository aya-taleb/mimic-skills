import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(__file__))
from _load import load  # noqa: E402

bugs = load("mimic-test", "bugs")

HEAD = ("| id | title | severity | status | flow | found | steps |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n")


class BugsTest(unittest.TestCase):
    def check(self, body):
        rows, problems = bugs.parse("# Bugs\n\n" + HEAD + body)
        return bugs.summary(rows, problems)

    def test_open_s1_blocks(self):
        s = self.check("| B001 | Double booking | S1 | open | F01 | 2026-10-20 | 1. two tabs |\n")
        self.assertTrue(s["deploy_blocked"])
        self.assertEqual(s["blockers"][0]["id"], "B001")

    def test_fixed_but_not_verified_still_blocks(self):
        s = self.check("| B001 | Double booking | S2 | fixed | F01 | 2026-10-20 | 1. x |\n")
        self.assertTrue(s["deploy_blocked"])

    def test_verified_and_minor_pass(self):
        s = self.check("| B001 | Double booking | S1 | verified | F01 | 2026-10-20 | 1. x |\n"
                       "| B002 | Button off by 2px | S4 | open | F02 | 2026-10-20 | 1. y |\n")
        self.assertFalse(s["deploy_blocked"])
        self.assertEqual(s["by_severity"]["S4"]["open"], 1)

    def test_bad_values_are_problems(self):
        s = self.check("| B001 | Thing | S9 | maybe | F01 | | 1. x |\n"
                       "| B001 | Other | S1 | wontfix | F01 | | 1. y |\n"
                       "| B003 | No steps | S3 | open | F01 | | |\n")
        text = " ".join(s["problems"])
        self.assertIn("S9", text)
        self.assertIn("maybe", text)
        self.assertIn("cannot be wontfix", text)
        self.assertIn("duplicate id", text)
        self.assertIn("no steps", text)
        self.assertTrue(s["deploy_blocked"])

    def test_no_table(self):
        with self.assertRaises(bugs.BugLogError):
            bugs.parse("nothing here")

    def test_empty_log_passes(self):
        s = self.check("")
        self.assertFalse(s["deploy_blocked"])

    def test_cli_gate(self):
        tmp = tempfile.mkdtemp()
        p = os.path.join(tmp, "bugs.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(HEAD + "| B001 | Broken | S2 | open | F01 | | 1. x |\n")
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(bugs.main([p, "--gate"]), 1)
        self.assertIn("Deploy blocked", out.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(bugs.main([p]), 0)
            self.assertEqual(bugs.main([os.path.join(tmp, "none.md")]), 2)


if __name__ == "__main__":
    unittest.main()
