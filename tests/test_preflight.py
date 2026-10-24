import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(__file__))
from _load import load  # noqa: E402

preflight = load("mimic-deploy", "preflight")

FAKE_SWEEP = '''import json, sys
root = sys.argv[1]
hits = []
import os
for d, _, fs in os.walk(root):
    for f in fs:
        p = os.path.join(d, f)
        try:
            text = open(p, encoding="utf-8").read()
        except Exception:
            continue
        if "Acme" in text and not p.endswith("brand.json"):
            hits.append({"file": os.path.relpath(p, root), "line": 1, "match": "Acme"})
print(json.dumps(hits))
sys.exit(1 if hits else 0)
'''


def touch(root, rel, text="x\n"):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


POLICY_BODY = " ".join(
    "We collect the name and email a guest types when they book, and the host's account "
    "details. We use them only to run bookings and send reminders. You can ask us to delete "
    "your data at any time by writing to the address below, and we answer within thirty days."
    .split()) + " "
PRIVACY = ("export default function Privacy() { return <main><h1>Privacy policy</h1><p>"
           + POLICY_BODY * 4 + "</p><h2>Who processes your data</h2><p>We share data only with "
           "the service providers that run the product: {procs}.</p></main>; }\n")
TERMS = ("export default function Terms() { return <main><h1>Terms of service</h1><p>"
         + ("By using Slotly you agree to these terms. The service is offered as it is, and we "
            "may change these terms with notice by email. You may cancel at any time from the "
            "billing page, and we refund the unused part of a yearly plan. ") * 4
         + "</p></main>; }\n")


def by_check(r):
    return {c["check"]: c for c in r["checks"]}


class PreflightTest(unittest.TestCase):
    def setUp(self):
        self.proj = tempfile.mkdtemp()
        self.linked = tempfile.mkdtemp()

    def ready_project(self):
        p = self.proj
        touch(p, "mimic/test/bugs.md", "| id | title | severity | status |\n"
                                       "| --- | --- | --- | --- |\n| B1 | x | S1 | verified |\n")
        touch(p, "mimic/features.csv", "feature,priority,original,clone\nbook,must,yes,yes\n"
                                       "catalogue,must,yes,skip\nteams,could,yes,no\n")
        touch(p, "mimic/brand.json", json.dumps({"avoid": ["Acme"]}))
        touch(p, "mimic/recon.md", "Acme does bookings.\n")
        touch(p, "mimic/launch/listing.json", json.dumps({"avoid": ["Acme"], "google_business": {
            "name": "Slotly", "description": "Booking links for small teams."}}))
        touch(p, "mimic/launch/landing.md", "# Book in two taps\n")
        touch(p, "mimic/backend.md", "| item | result | how |\n| --- | --- | --- |\n"
                                     "| access checks | pass | tested A vs B |\n")
        touch(p, "app/privacy/page.tsx", PRIVACY.replace("{procs}", "our hosting provider"))
        touch(p, "app/terms/page.tsx", TERMS)
        touch(p, ".gitignore", "node_modules\n.env\n")
        touch(p, "app/page.tsx", "export default function Page() { return 'Slotly' }\n")
        touch(self.linked, "replica-brand/SKILL.md", "---\nname: replica-brand\n---\n")
        touch(self.linked, "replica-brand/sweep.py", FAKE_SWEEP)

    def run_pf(self):
        return preflight.preflight(self.proj, [self.linked])

    def test_ready_project_passes(self):
        self.ready_project()
        r = self.run_pf()
        self.assertEqual(r["blocked_by"], [], json.dumps(by_check(r), indent=1))
        self.assertEqual(r["verdict"], "ready for the user's go")
        self.assertEqual(by_check(r)["payments"]["status"], "ask")

    def test_empty_project_blocked_with_not_run(self):
        r = preflight.preflight(self.proj, [self.linked])
        c = by_check(r)
        self.assertEqual(c["bugs"]["status"], "not run")
        self.assertEqual(c["sweep"]["status"], "not run")
        self.assertIn("bugs", r["blocked_by"])

    def test_sweep_not_installed_names_get_linked(self):
        self.ready_project()
        shutil.rmtree(os.path.join(self.linked, "replica-brand"))
        home = os.environ.get("HOME")
        os.environ["HOME"] = tempfile.mkdtemp()
        try:
            c = by_check(self.run_pf())["sweep"]
        finally:
            os.environ["HOME"] = home
        self.assertEqual(c["status"], "not run")
        self.assertIn("get_linked.py", c["detail"])

    def test_leftover_outside_mimic_fails_sweep(self):
        self.ready_project()
        touch(self.proj, "app/embed.tsx", "export const AcmeEmbed = 1\n")
        c = by_check(self.run_pf())["sweep"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("app/embed.tsx", c["output"])

    def test_open_s2_blocks(self):
        self.ready_project()
        touch(self.proj, "mimic/test/bugs.md", "| id | title | severity | status |\n"
                                               "| --- | --- | --- | --- |\n| B2 | x | S2 | open |\n")
        self.assertIn("bugs", self.run_pf()["blocked_by"])

    def test_missing_must_feature_blocks(self):
        self.ready_project()
        touch(self.proj, "mimic/features.csv", "feature,priority,original,clone\n"
                                               "book,must,yes,partial\n")
        c = by_check(self.run_pf())["parity"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("book", c["detail"])

    def test_secret_in_code_fails(self):
        self.ready_project()
        touch(self.proj, "lib/pay.ts", "const k = 'sk_live_" + "a" * 24 + "'\n")
        c = by_check(self.run_pf())["secrets"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("lib/pay.ts", c["output"])

    def test_placeholder_assignment_is_fine(self):
        self.assertEqual(preflight.scan_secrets(
            [touch(self.proj, "a.ts", "apiKey: 'your-api-key-here-please'\n")], self.proj), [])

    def test_env_not_ignored_fails(self):
        self.ready_project()
        touch(self.proj, ".gitignore", "node_modules\n")
        self.assertEqual(by_check(self.run_pf())["secrets"]["status"], "fail")

    def test_unconfirmed_proof_fails_launch(self):
        self.ready_project()
        touch(self.proj, "mimic/launch/landing.md", "# Hero\nTrusted by 900 teams\n")
        c = by_check(self.run_pf())["launch"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("proof", c["detail"])

    def test_security_fail_blocks(self):
        self.ready_project()
        touch(self.proj, "mimic/backend.md", "| item | result | how |\n| --- | --- | --- |\n"
                                             "| rate limits | fail | none yet |\n")
        self.assertIn("security", self.run_pf()["blocked_by"])

    def test_missing_terms_fails_legal(self):
        self.ready_project()
        os.remove(os.path.join(self.proj, "app/terms/page.tsx"))
        c = by_check(self.run_pf())["legal"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("terms", c["detail"])

    def test_one_line_legal_pages_fail(self):
        self.ready_project()
        touch(self.proj, "app/privacy/page.tsx",
              "export default function P() { return <main><h1>Privacy policy</h1>"
              "<p>Draft from the founder's lawyer.</p></main>; }\n")
        touch(self.proj, "app/terms/page.tsx", "export default 1\n")
        c = by_check(self.run_pf())["legal"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("stub", c["detail"])
        self.assertIn("terms page", c["detail"])

    def test_privacy_must_name_processors(self):
        self.ready_project()
        touch(self.proj, "package.json", json.dumps(
            {"dependencies": {"next": "14", "@supabase/supabase-js": "2", "stripe": "16"}}))
        touch(self.proj, ".env.example", "RESEND_API_KEY=\nTWILIO_AUTH_TOKEN=\n")
        touch(self.proj, "app/privacy/page.tsx", PRIVACY.replace("{procs}", "Supabase (database), Stripe (payments)"))
        c = by_check(self.run_pf())["legal"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("Resend", c["detail"])
        self.assertIn("Twilio", c["detail"])
        self.assertNotIn("Stripe (", c["detail"])
        touch(self.proj, "app/privacy/page.tsx",
              PRIVACY.replace("{procs}", "Supabase, Stripe, Resend (email) and Twilio (text messages)"))
        c = by_check(self.run_pf())["legal"]
        self.assertEqual(c["status"], "pass", c["detail"])
        self.assertIn("Twilio", c["detail"])

    def test_legal_placeholder_fails(self):
        self.ready_project()
        touch(self.proj, "app/terms/page.tsx", TERMS.replace("Slotly", "{{company name}}"))
        c = by_check(self.run_pf())["legal"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("placeholder", c["detail"])

    def test_privacy_without_sharing_section_fails(self):
        self.ready_project()
        touch(self.proj, "app/privacy/page.tsx",
              "export default function P() { return <main><p>" + POLICY_BODY * 5 + "</p></main>; }\n")
        c = by_check(self.run_pf())["legal"]
        self.assertEqual(c["status"], "fail")
        self.assertIn("who processes", c["detail"])

    def test_cli_writes_report(self):
        self.ready_project()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = preflight.main(["--project", self.proj, "--linked-dir", self.linked])
        self.assertEqual(code, 0)
        with open(os.path.join(self.proj, "mimic/deploy/preflight.md"), encoding="utf-8") as fh:
            report = fh.read()
        self.assertIn("ready for the user's go", report)


if __name__ == "__main__":
    unittest.main()
