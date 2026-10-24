#!/usr/bin/env python3
"""Preflight gate for mimic-deploy. Standard library only, no network.

Runs the checks that must pass before anything goes live, and writes the result
to mimic/deploy/preflight.md. It never deploys anything. Going live is the
user's call, after they have read this.

    python3 preflight.py --project .
    python3 preflight.py --project . --linked-dir ~/.claude/skills
    python3 preflight.py --project . --json

Checks:
  bugs        no open S1 or S2 in mimic/test/bugs.md  (uses mimic-test's bugs.py)
  parity      every must feature built, per mimic/features.csv
              (and the linked replica-diff parity.py score if it is installed)
  sweep       nothing of the competitors left in the code
              (the linked replica-brand sweep.py with mimic/brand.json)
  secrets     no keys or tokens in tracked files, .env ignored by git
  launch      mimic/launch/listing.json passes listing.py, no unchecked proof
  security    no "fail" left in the checklist in mimic/backend.md
  legal       a real privacy policy and terms page: present, at least 150 words each, no
              placeholders, and the privacy policy names every processor the project
              uses (from package.json, requirements.txt, .env.example names, host files)
  payments    a note on live mode: asked, never assumed

A check that cannot run (a tool not installed, a file missing) is "not run",
and the gate does not pass while any blocking check is not run.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(SKILLS, ".."))
BUGS_TOOL = os.path.join(SKILLS, "mimic-test", "scripts", "bugs.py")
LISTING_TOOL = os.path.join(SKILLS, "mimic-launch", "scripts", "listing.py")

SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "out", ".venv", "venv",
             "__pycache__", ".turbo", ".cache", "coverage", "mimic", ".expo", "Pods"}
TEXT_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".go", ".java",
            ".kt", ".swift", ".json", ".yml", ".yaml", ".toml", ".env", ".sh", ".md",
            ".html", ".css", ".vue", ".svelte", ".php", ".ini", ".cfg", ".txt", ""}
SECRET_PATTERNS = [
    ("stripe live secret key", re.compile(r"\bsk_live_[0-9A-Za-z]{10,}")),
    ("stripe restricted key", re.compile(r"\brk_live_[0-9A-Za-z]{10,}")),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{30,}\b")),
    ("slack token", re.compile(r"\bxox[abpr]-[0-9A-Za-z-]{10,}")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("private key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("openai or anthropic key", re.compile(r"\bsk-(ant-)?[A-Za-z0-9_\-]{30,}")),
    ("replicate token", re.compile(r"\br8_[0-9A-Za-z]{30,}")),
]
ASSIGNED = re.compile(r"(?i)\b(secret|password|passwd|api[_-]?key|token)\b\s*[:=]\s*['\"]([^'\"\s]{12,})['\"]")
PLACEHOLDER = re.compile(r"(?i)(your|example|xxx|changeme|placeholder|dummy|test|<|\{\{|\$\{|process\.env)")


def rel(project, path):
    return os.path.relpath(path, project)


def run_tool(args, cwd):
    try:
        p = subprocess.run([sys.executable, "-I"] + args, cwd=cwd, capture_output=True,
                           text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    return p.returncode, (p.stdout + p.stderr).strip()


def result(check, status, detail, blocking=True, output=""):
    return {"check": check, "status": status, "detail": detail,
            "blocking": blocking, "output": output[-1500:]}


def check_bugs(project):
    log = os.path.join(project, "mimic", "test", "bugs.md")
    if not os.path.isfile(log):
        return result("bugs", "not run", "no mimic/test/bugs.md. Run /mimic-test first.")
    if not os.path.isfile(BUGS_TOOL):
        return result("bugs", "not run", "mimic-test's bugs.py not found next to this skill")
    code, out = run_tool([BUGS_TOOL, log, "--gate"], project)
    if code == 0:
        return result("bugs", "pass", "no open S1 or S2", output=out)
    if code == 1:
        return result("bugs", "fail", "open S1/S2 bugs or an incomplete log", output=out)
    return result("bugs", "not run", "bugs.py could not read the log", output=out)


def find_linked(name, project, linked_dirs):
    places = list(linked_dirs) + [os.path.join(project, ".claude", "skills"),
                                  os.path.expanduser("~/.claude/skills")]
    for base in places:
        folder = os.path.join(os.path.expanduser(base), name)
        if os.path.isfile(os.path.join(folder, "SKILL.md")):
            return folder
    return None


def check_parity(project, linked_dirs):
    path = os.path.join(project, "mimic", "features.csv")
    if not os.path.isfile(path):
        return result("parity", "not run", "no mimic/features.csv. Run /mimic-recon first.")
    missing = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            if row.get("priority", "").lower() not in ("must", "p0"):
                continue
            if row.get("clone", "").lower() in ("yes", "done", "skip"):
                continue
            missing.append(row.get("feature", "?"))
    out = ""
    diff = find_linked("replica-diff", project, linked_dirs)
    if diff and os.path.isfile(os.path.join(diff, "parity.py")):
        _, out = run_tool([os.path.join(diff, "parity.py"), path], project)
    note = "" if diff else " (replica-diff not installed, so no parity score: python3 scripts/get_linked.py)"
    if missing:
        return result("parity", "fail", "%d must feature(s) not built: %s%s"
                      % (len(missing), "; ".join(missing[:8]), note), output=out)
    return result("parity", "pass", "every must feature is built%s" % note, output=out)


def check_sweep(project, linked_dirs):
    cfg = os.path.join(project, "mimic", "brand.json")
    if not os.path.isfile(cfg):
        return result("sweep", "not run", "no mimic/brand.json. Run /replica-brand first.")
    brand = find_linked("replica-brand", project, linked_dirs)
    tool = os.path.join(brand, "sweep.py") if brand else None
    if not tool or not os.path.isfile(tool):
        return result("sweep", "not run", "replica-brand (linked) is not installed. "
                      "Install it with: python3 %s" % os.path.join(REPO, "scripts", "get_linked.py"))
    # sweep.py skips a top-level replica/ folder but not mimic/, where competitor
    # names belong (recon, reviews). Drop hits inside mimic/ after the sweep.
    code, out = run_tool([tool, project, "--config", cfg, "--json"], project)
    if code not in (0, 1):
        return result("sweep", "not run", "sweep.py failed", output=out)
    try:
        hits = json.loads(out) if out.strip().startswith("[") else []
    except ValueError:
        return result("sweep", "not run", "could not read sweep.py output", output=out)
    hits = [h for h in hits if not h.get("file", "").startswith("mimic" + os.sep)
            and not h.get("file", "").startswith("mimic/")]
    if hits:
        lines = ["%s:%s %s" % (h["file"], h.get("line", 0), h.get("match", "")) for h in hits[:20]]
        return result("sweep", "fail", "%d leftover(s) of the competitors" % len(hits),
                      output="\n".join(lines))
    return result("sweep", "pass", "nothing of the competitors found outside mimic/")


def git_tracked(project):
    try:
        p = subprocess.run(["git", "-C", project, "ls-files"], capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    return [os.path.join(project, f) for f in p.stdout.splitlines() if f.strip()]


def walk_files(project):
    for dirpath, dirnames, filenames in os.walk(project):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            yield os.path.join(dirpath, f)


def scan_secrets(paths, project):
    hits = []
    for path in paths:
        name = os.path.basename(path)
        ext = os.path.splitext(name)[1].lower()
        if name.startswith(".env") and name != ".env.example":
            hits.append("%s: an env file with real values should not be tracked" % rel(project, path))
            continue
        if ext not in TEXT_EXT and not name.startswith(".env"):
            continue
        try:
            if os.path.getsize(path) > 1_000_000:
                continue
            with open(path, encoding="utf-8", errors="ignore") as fh:
                for n, line in enumerate(fh, 1):
                    for label, rx in SECRET_PATTERNS:
                        if rx.search(line):
                            hits.append("%s:%d %s" % (rel(project, path), n, label))
                    m = ASSIGNED.search(line)
                    if m and not PLACEHOLDER.search(m.group(2)):
                        hits.append("%s:%d %s assigned in code" % (rel(project, path), n,
                                                                  m.group(1).lower()))
        except OSError:
            continue
    return hits


def check_secrets(project):
    tracked = git_tracked(project)
    paths = tracked if tracked is not None else list(walk_files(project))
    paths = [p for p in paths if not rel(project, p).startswith("mimic" + os.sep)]
    hits = scan_secrets(paths, project)
    gitignore = os.path.join(project, ".gitignore")
    ignored = False
    if os.path.isfile(gitignore):
        with open(gitignore, encoding="utf-8", errors="ignore") as fh:
            ignored = any(re.match(r"^\s*/?\.env(\*|\.\*|\.local)?\s*$", l) for l in fh)
    if not ignored:
        hits.append(".gitignore does not ignore .env")
    scope = "tracked files" if tracked is not None else "all files (not a git repo)"
    if hits:
        return result("secrets", "fail", "%d possible secret(s) in %s" % (len(hits), scope),
                      output="\n".join(hits[:20]))
    return result("secrets", "pass", "no keys found in %s, .env is ignored" % scope)


def check_launch(project):
    listing = os.path.join(project, "mimic", "launch", "listing.json")
    landing = os.path.join(project, "mimic", "launch", "landing.md")
    if not os.path.isfile(listing):
        return result("launch", "not run", "no mimic/launch/listing.json. Run /mimic-launch.")
    args = [LISTING_TOOL, listing]
    if os.path.isfile(landing):
        args += ["--proof", landing]
    code, out = run_tool(args, project)
    if code is None or code == 2:
        return result("launch", "not run", "listing.py could not run", output=out or "")
    proof = [l for l in out.splitlines() if "proof claim" in l]
    if code == 1:
        return result("launch", "fail", "listing.py found errors", output=out)
    if proof:
        return result("launch", "fail", "%d proof claim(s) not confirmed. Cut them, or add "
                      "them to proof_ok in listing.json once you have the source and "
                      "permission" % len(proof), output=out)
    return result("launch", "pass", "listing and landing copy pass", output=out)


def check_security(project):
    path = os.path.join(project, "mimic", "backend.md")
    if not os.path.isfile(path):
        return result("security", "not run", "no mimic/backend.md. Run /mimic-backend.")
    with open(path, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    fails = [l.strip() for l in text.splitlines()
             if l.strip().startswith("|") and re.search(r"\|\s*fail\s*\|", l, re.I)]
    unchecked = [l for l in text.splitlines()
                 if l.strip().startswith("|") and re.search(r"\|\s*not checked\s*\|", l, re.I)]
    if fails:
        return result("security", "fail", "%d checklist item(s) marked fail" % len(fails),
                      output="\n".join(fails[:15]))
    detail = "no fails in the checklist"
    if unchecked:
        detail += "; %d not checked (review them before launch)" % len(unchecked)
    return result("security", "pass", detail)


LEGAL = {"privacy": re.compile(r"(^|[/_.-])privacy([/_.-]|$)"),
         "terms": re.compile(r"(^|[/_.-])(terms|tos)([/_.-]|$)")}
PAGE_EXT = (".md", ".mdx", ".html", ".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".astro")
LEGAL_MIN_WORDS = 150
LEGAL_PLACEHOLDER = re.compile(r"(?i)(\{\{|lorem ipsum|\bTODO\b|\bTBD\b|coming soon|\[company name\]|"
                               r"\[your )")
SHARING_WORDS = re.compile(r"(?i)(processor|service provider|third[- ]part|we share|shared with)")
CODE_WORDS = {"export", "default", "function", "return", "const", "import", "from", "main",
              "classname", "class", "div", "span", "section", "props", "metadata", "async",
              "await", "let", "var", "null", "true", "false", "undefined", "type", "interface",
              "string", "number", "react", "next", "href", "link", "page", "layout", "html",
              "body", "head", "title", "script", "style", "template", "jsx", "tsx"}

# Processors a privacy policy must name when the project uses them. Each entry:
# name, package prefixes (package.json or requirements.txt), env var prefixes, host files.
PROCESSORS = [
    ("Stripe", ("stripe", "@stripe/"), ("STRIPE_",), ()),
    ("Supabase", ("@supabase/", "supabase"), ("SUPABASE_", "NEXT_PUBLIC_SUPABASE_"), ()),
    ("Firebase", ("firebase", "firebase-admin"), ("FIREBASE_", "NEXT_PUBLIC_FIREBASE_"), ()),
    ("Clerk", ("@clerk/",), ("CLERK_", "NEXT_PUBLIC_CLERK_"), ()),
    ("Auth0", ("auth0", "@auth0/"), ("AUTH0_",), ()),
    ("Paddle", ("@paddle/",), ("PADDLE_",), ()),
    ("Lemon Squeezy", ("@lemonsqueezy/",), ("LEMONSQUEEZY_", "LEMON_SQUEEZY_"), ()),
    ("Resend", ("resend",), ("RESEND_",), ()),
    ("SendGrid", ("@sendgrid/", "sendgrid"), ("SENDGRID_",), ()),
    ("Postmark", ("postmark",), ("POSTMARK_",), ()),
    ("Mailgun", ("mailgun", "mailgun.js"), ("MAILGUN_",), ()),
    ("Twilio", ("twilio",), ("TWILIO_",), ()),
    ("Sentry", ("@sentry/", "sentry-sdk"), ("SENTRY_", "NEXT_PUBLIC_SENTRY_"), ()),
    ("PostHog", ("posthog-js", "posthog-node", "posthog"), ("POSTHOG_", "NEXT_PUBLIC_POSTHOG_"), ()),
    ("Mixpanel", ("mixpanel", "mixpanel-browser"), ("MIXPANEL_",), ()),
    ("Segment", ("@segment/",), ("SEGMENT_",), ()),
    ("Plausible", ("plausible-tracker", "next-plausible"), ("PLAUSIBLE_",), ()),
    ("Google Analytics", ("react-ga4", "@next/third-parties"), ("NEXT_PUBLIC_GA_", "GA_MEASUREMENT"), ()),
    ("OpenAI", ("openai",), ("OPENAI_",), ()),
    ("Anthropic", ("@anthropic-ai/", "anthropic"), ("ANTHROPIC_",), ()),
    ("Replicate", ("replicate",), ("REPLICATE_",), ()),
    ("Amazon Web Services", ("aws-sdk", "@aws-sdk/", "boto3"), ("AWS_",), ()),
    ("Cloudinary", ("cloudinary",), ("CLOUDINARY_",), ()),
    ("Upstash", ("@upstash/",), ("UPSTASH_",), ()),
    ("Neon", ("@neondatabase/",), ("NEON_",), ()),
    ("Vercel", ("@vercel/analytics", "@vercel/speed-insights"), ("VERCEL_",), ("vercel.json",)),
    ("Netlify", (), ("NETLIFY_",), ("netlify.toml",)),
    ("Render", (), (), ("render.yaml",)),
    ("Fly.io", (), (), ("fly.toml",)),
    ("Railway", (), (), ("railway.json", "railway.toml")),
]


def page_text(path):
    """The readable words of a page: tags, code keywords and punctuation removed."""
    with open(path, encoding="utf-8", errors="ignore") as fh:
        raw = fh.read()
    raw = re.sub(r"(?m)^\s*(import|export\s+const\s+metadata)\b.*$", " ", raw)
    raw = re.sub(r"<[^>]*>", " ", raw)
    return raw


def word_count(text):
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", text)
    return len([w for w in words if w.lower() not in CODE_WORDS])


def project_deps(project):
    """Package names from package.json (all dependency kinds) and requirements.txt."""
    deps = set()
    pj = os.path.join(project, "package.json")
    if os.path.isfile(pj):
        try:
            with open(pj, encoding="utf-8") as fh:
                data = json.load(fh)
            for key in ("dependencies", "devDependencies", "optionalDependencies"):
                deps.update(k.lower() for k in (data.get(key) or {}))
        except (OSError, ValueError):
            pass
    req = os.path.join(project, "requirements.txt")
    if os.path.isfile(req):
        with open(req, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                name = re.split(r"[<>=\[;\s]", line.strip(), 1)[0].lower()
                if name and not name.startswith("#"):
                    deps.add(name)
    return deps


def project_env_names(project):
    """Variable names from .env.example and similar files (names only, never values)."""
    names = set()
    for f in os.listdir(project):
        if f.startswith(".env") or f in ("env.example", "example.env"):
            try:
                with open(os.path.join(project, f), encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        m = re.match(r"\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=", line)
                        if m:
                            names.add(m.group(1))
            except OSError:
                continue
    return names


def detect_processors(project):
    """Return [(processor name, why)] for the services the project's code or config uses."""
    deps = project_deps(project)
    env = project_env_names(project)
    found = []
    for name, pkgs, prefixes, files in PROCESSORS:
        why = None
        for d in sorted(deps):
            if any(d == p or (p.endswith("/") and d.startswith(p)) for p in pkgs):
                why = "package %s" % d
                break
        if not why:
            hit = sorted(e for e in env if any(e.startswith(p) for p in prefixes))
            if hit:
                why = "env %s" % hit[0]
        if not why:
            hit = [f for f in files if os.path.exists(os.path.join(project, f))]
            if hit:
                why = "file %s" % hit[0]
        if why:
            found.append((name, why))
    return found


def names_in(text, name):
    squash = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    if squash(name) in squash(text):
        return True
    return name == "Amazon Web Services" and re.search(r"\bAWS\b", text) is not None


def check_legal(project):
    """A real privacy policy and terms page: present, not a stub, and naming the processors.

    A one-line page passes a file-name check and protects nobody, so the page text must
    have at least LEGAL_MIN_WORDS words, no placeholders, and (privacy) name every
    processor the code or config uses.
    """
    pages = {"privacy": [], "terms": []}
    for path in walk_files(project):
        low = rel(project, path).lower().replace("\\", "/")
        if not low.endswith(PAGE_EXT):
            continue
        for key, rx in LEGAL.items():
            if rx.search(low):
                pages[key].append(path)
    missing = [k for k, v in pages.items() if not v]
    advice = ("Not legal advice: have a lawyer or a reputable generator draft them for your "
              "country, then put the full text on the page")
    if missing:
        return result("legal", "fail", "no %s page found in the project. %s"
                      % (" or ".join(missing), advice))
    problems = []
    texts = {}
    for key, paths in pages.items():
        text = "\n".join(page_text(p) for p in sorted(paths))
        texts[key] = text
        shown = ", ".join(rel(project, p) for p in sorted(paths))
        n = word_count(text)
        if n < LEGAL_MIN_WORDS:
            problems.append("%s page (%s) has %d words, a stub, not a real %s"
                            % (key, shown, n, "privacy policy" if key == "privacy" else "terms page"))
        if LEGAL_PLACEHOLDER.search(text):
            problems.append("%s page (%s) still has placeholder text" % (key, shown))
    processors = detect_processors(project)
    unnamed = [(n, why) for n, why in processors if not names_in(texts["privacy"], n)]
    if unnamed:
        problems.append("privacy policy does not name: %s"
                        % ", ".join("%s (%s)" % (n, why) for n, why in unnamed))
    if not processors and not SHARING_WORDS.search(texts["privacy"]):
        problems.append("privacy policy says nothing about who processes the data "
                        "(no processors found in package.json or env names; list them by hand)")
    if problems:
        return result("legal", "fail", "; ".join(problems) + ". " + advice,
                      output="\n".join(problems))
    named = ", ".join(n for n, _ in processors) or "none detected, sharing section present"
    return result("legal", "pass", "privacy: %s, terms: %s, processors named: %s" % (
        rel(project, sorted(pages["privacy"])[0]), rel(project, sorted(pages["terms"])[0]), named))


def payments_note():
    return result("payments", "ask", "Confirm with the user: live keys set in the host, live "
                  "webhook endpoint added, one real low-value payment refunded. This tool "
                  "cannot see the host's settings.", blocking=False)


def preflight(project, linked_dirs=()):
    project = os.path.abspath(project)
    checks = [check_bugs(project), check_parity(project, linked_dirs),
              check_sweep(project, linked_dirs), check_secrets(project),
              check_launch(project), check_security(project), check_legal(project),
              payments_note()]
    blocking = [c for c in checks if c["blocking"] and c["status"] != "pass"]
    return {"project": project, "checks": checks,
            "verdict": "ready for the user's go" if not blocking else "blocked",
            "blocked_by": [c["check"] for c in blocking]}


def render(r):
    out = ["# Preflight", "", "Project: %s" % r["project"], "",
           "| check | result | detail |", "| --- | --- | --- |"]
    for c in r["checks"]:
        out.append("| %s | %s | %s |" % (c["check"], c["status"], c["detail"].replace("|", "/")))
    out.append("")
    if r["blocked_by"]:
        out.append("Verdict: blocked by %s. Nothing goes live until these pass."
                   % ", ".join(r["blocked_by"]))
    else:
        out.append("Verdict: ready for the user's go. Ask before deploying.")
    for c in r["checks"]:
        if c["output"]:
            out += ["", "## %s output" % c["check"], "", "```", c["output"], "```"]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", default=".")
    ap.add_argument("--linked-dir", action="append", default=[],
                    help="a folder with the linked replica-* skills installed")
    ap.add_argument("--out", help="write the report here (default mimic/deploy/preflight.md)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.project):
        print("preflight: %s is not a folder" % args.project, file=sys.stderr)
        return 2
    r = preflight(args.project, args.linked_dir)
    text = render(r)
    out = args.out or os.path.join(args.project, "mimic", "deploy", "preflight.md")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(json.dumps(r, indent=2) if args.json else text)
    print("wrote %s" % out, file=sys.stderr)
    return 0 if not r["blocked_by"] else 1


if __name__ == "__main__":
    sys.exit(main())
