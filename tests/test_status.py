import io
import os
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(__file__))
from _load import load  # noqa: E402

status = load("mimic-run", "status")


def touch(root, rel, text="x\n"):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class StatusTest(unittest.TestCase):
    def setUp(self):
        self.proj = tempfile.mkdtemp()
        self.home = tempfile.mkdtemp()
        self.fh = tempfile.mkdtemp()
        self._env = mock.patch.dict(os.environ, {"FOUNDER_HOME": self.fh})
        self._env.start()
        self.addCleanup(self._env.stop)

    def run_status(self):
        return status.status(self.proj, home=self.home)

    def test_empty_project_starts_with_recon(self):
        r = self.run_status()
        self.assertEqual(r["next"], "mimic-recon")
        self.assertIsNone(r["founder_context"])
        self.assertTrue(any("business context" in w for w in r["warnings"]))
        self.assertEqual([o["skill"] for o in r["optional_before"]],
                         ["market-research", "competitors"])

    def test_optional_not_offered_once_recon_started(self):
        touch(self.proj, "mimic/recon.md")
        self.assertEqual(self.run_status()["optional_before"], [])

    def test_partial_step_reported(self):
        touch(self.proj, "mimic/recon.md")
        r = self.run_status()
        recon = next(s for s in r["steps"] if s["id"] == "recon")
        self.assertEqual(recon["state"], "partial")
        self.assertEqual(recon["missing"], ["mimic/features.csv"])
        self.assertEqual(r["next"], "mimic-recon")

    def test_after_reviews_next_is_validate(self):
        for f in ("mimic/recon.md", "mimic/features.csv", "mimic/reviews.csv", "mimic/fixes.md"):
            touch(self.proj, f)
        self.assertEqual(self.run_status()["next"], "validate")

    def test_failed_validate_sets_gate(self):
        for f in ("mimic/recon.md", "mimic/features.csv", "mimic/reviews.csv", "mimic/fixes.md"):
            touch(self.proj, f)
        touch(self.proj, "founder/validate.md", "# Validate\n\nVerdict: stop. Nobody signed up.\n")
        r = self.run_status()
        self.assertEqual(r["validate_verdict"], "stop")
        self.assertIn("demand test", r["gate"])
        self.assertEqual(r["next"], "mimic-architect")

    def test_passed_validate_no_gate(self):
        touch(self.proj, "founder/validate.md", "Decision: go\n")
        self.assertEqual(status.validate_verdict(self.proj), "go")
        touch(self.proj, "founder/validate.md", "- **Result:** passed both lines\n")
        self.assertEqual(status.validate_verdict(self.proj), "go")

    def test_linked_skill_missing_blocks_next(self):
        for f in ("mimic/recon.md", "mimic/features.csv", "mimic/reviews.csv",
                  "mimic/fixes.md", "mimic/architecture.md",
                  "mimic/build-log.md", "mimic/backend.md", "mimic/test/plan.md"):
            touch(self.proj, f)
        touch(self.proj, "founder/validate.md", "Result: go\n")
        touch(self.proj, "mimic/test/bugs.md",
              "| id | title | severity | status |\n| --- | --- | --- | --- |\n")
        r = self.run_status()
        self.assertEqual(r["next"], "replica-diff")
        self.assertIn("get_linked.py", r["next_blocked"])
        self.assertIn("get_linked.py", status.render(r))

    def test_validate_plan_without_result_is_not_done(self):
        for f in ("mimic/recon.md", "mimic/features.csv", "mimic/reviews.csv", "mimic/fixes.md",
                  "mimic/architecture.md"):
            touch(self.proj, f)
        touch(self.proj, "founder/validate.md", "# Validate\n\nTest: deposit page. Pass line: 20 to 30.\n")
        r = self.run_status()
        v = next(s for s in r["steps"] if s["id"] == "validate")
        self.assertEqual(v["state"], "partial")
        self.assertEqual(r["next"], "validate")
        self.assertIn("numbers", r["next_reason"])
        touch(self.proj, "founder/validate.md", "# Validate\n\nResult: go, 27 deposits.\n")
        r = self.run_status()
        self.assertEqual(next(s for s in r["steps"] if s["id"] == "validate")["state"], "done")
        self.assertNotEqual(r["next"], "validate")

    def test_linked_skill_found_in_home(self):
        touch(self.home, ".claude/skills/replica-diff/SKILL.md", "---\nname: replica-diff\n---\n")
        r = self.run_status()
        self.assertTrue(r["linked"]["replica-diff"])
        self.assertFalse(r["linked"]["replica-brand"])

    def test_open_s1_blocks_deploy(self):
        touch(self.proj, "mimic/test/bugs.md",
              "| id | title | severity | status |\n| --- | --- | --- | --- |\n"
              "| B1 | broken | S1 | open |\n| B2 | ok now | S2 | verified |\n")
        self.assertEqual(status.open_blockers(self.proj), 1)
        self.assertIn("S1 or S2", self.run_status()["gate"])

    def chain_to_architect(self, recon_text):
        touch(self.proj, "mimic/recon.md", recon_text)
        for f in ("mimic/features.csv", "mimic/reviews.csv", "mimic/fixes.md",
                  "mimic/architecture.md"):
            touch(self.proj, f)
        touch(self.proj, "founder/validate.md", "Result: go\n")

    def test_app_needs_design_next(self):
        self.chain_to_architect("# Recon\nType: app or website\n")
        r = self.run_status()
        self.assertEqual(r["business_type"], "app")
        self.assertEqual(r["next"], "replica-design")
        self.assertIn("get_linked.py", r["next_blocked"])

    def test_local_business_skips_design(self):
        self.chain_to_architect("# Recon\n**Type:** local business (lunch delivery)\n")
        r = self.run_status()
        self.assertEqual(r["business_type"], "offline")
        design = next(s for s in r["steps"] if s["id"] == "design")
        self.assertEqual(design["state"], "skip")
        self.assertEqual(r["next"], "mimic-build")
        self.assertIn("skipped", status.render(r))

    def test_unknown_type_template_placeholder(self):
        touch(self.proj, "mimic/recon.md", "Type: {{app or website | service}}\n")
        self.assertIsNone(status.business_type(self.proj))

    def test_founder_context_from_founder_home(self):
        touch(self.fh, "active", "lunch\n")
        touch(self.fh, "businesses/lunch.md", "# Lunch\n")
        r = self.run_status()
        self.assertEqual(r["active_business"], "lunch")
        self.assertEqual(r["founder_context"], os.path.join(self.fh, "businesses", "lunch.md"))

    def test_founder_context_default_is_dot_founder(self):
        os.environ.pop("FOUNDER_HOME")
        touch(self.home, ".founder/active", "lunch\n")
        touch(self.home, ".founder/businesses/lunch.md", "# Lunch\n")
        r = self.run_status()
        self.assertEqual(r["founder_context"],
                         os.path.join(self.home, ".founder", "businesses", "lunch.md"))

    def test_replica_folder_warning_and_features(self):
        os.makedirs(os.path.join(self.proj, "replica"))
        touch(self.proj, "mimic/features.csv",
              "feature,priority,original,clone\na,must,yes,yes\nb,must,yes,no\n"
              "c,must,no,no\nd,must,yes,skip\n")
        r = self.run_status()
        self.assertTrue(any("replica/" in w for w in r["warnings"]))
        self.assertEqual(r["features"], {"must_total": 2, "must_done": 1})

    def test_cli(self):
        with redirect_stdout(io.StringIO()) as out:
            code = status.main(["--project", self.proj, "--home", self.home])
        self.assertEqual(code, 0)
        self.assertIn("Next: /mimic-recon", out.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(status.main(["--project", os.path.join(self.proj, "nope")]), 2)


if __name__ == "__main__":
    unittest.main()
