#!/usr/bin/env python3
"""Where am I in the mimic chain? Standard library only, no network.

Reads the working files the mimic skills write in a project (mimic/ and founder/),
shows which steps are done, checks which linked and synced skills are installed,
and names the next step.

    python3 status.py                     # the project in the current folder
    python3 status.py --project ~/code/my-app
    python3 status.py --json
    python3 status.py --skills-dir /extra/place/with/skills

It only reads files. It never runs another skill and never touches the network.
"""

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# This file sits at <repo>/skills/mimic-run/scripts/status.py
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SKILLS_ROOT = os.path.join(REPO_ROOT, "skills")

LINKED = ("replica-design", "replica-diff", "replica-brand")
SYNCED = ("market-research", "competitors", "validate", "launch-video")

# The chain, in order. Each step: id, stage, skill, files that show it is done,
# and whether the chain can go on without it.
STEPS = [
    {"id": "market", "stage": "research", "skill": "market-research",
     "files": ["founder/market.md"], "optional": True,
     "why": "is the market big enough to bother"},
    {"id": "competitors", "stage": "research", "skill": "competitors",
     "files": ["founder/competitors.md"], "optional": True,
     "why": "which competitors to study"},
    {"id": "recon", "stage": "research", "skill": "mimic-recon",
     "files": ["mimic/recon.md", "mimic/features.csv"],
     "why": "what the competitors do, step by step"},
    {"id": "reviews", "stage": "reviews", "skill": "mimic-reviews",
     "files": ["mimic/reviews.csv", "mimic/fixes.md"],
     "why": "what their customers hate, so yours is better"},
    {"id": "validate", "stage": "validate", "skill": "validate",
     "files": ["founder/validate.md"],
     "why": "a cheap demand test before you build"},
    {"id": "architect", "stage": "build", "skill": "mimic-architect",
     "files": ["mimic/architecture.md"], "why": "stack, data and build order"},
    {"id": "design", "stage": "build", "skill": "replica-design", "linked": True,
     "files": ["mimic/design/tokens.json"], "apps_only": True,
     "why": "design tokens and component specs"},
    {"id": "build", "stage": "build", "skill": "mimic-build",
     "files": ["mimic/build-log.md"], "why": "build it slice by slice"},
    {"id": "backend", "stage": "build", "skill": "mimic-backend",
     "files": ["mimic/backend.md"], "why": "auth, payments, email, security"},
    {"id": "test", "stage": "build", "skill": "mimic-test",
     "files": ["mimic/test/plan.md", "mimic/test/bugs.md"],
     "why": "test plan, end to end tests, bug log"},
    {"id": "diff", "stage": "build", "skill": "replica-diff", "linked": True,
     "files": ["mimic/parity.md"], "why": "how close to the competitors, what is missing"},
    {"id": "brand", "stage": "build", "skill": "replica-brand", "linked": True,
     "files": ["mimic/brand.json"], "why": "your own name and look, and the leftover sweep"},
    {"id": "launch", "stage": "launch", "skill": "mimic-launch",
     "files": ["mimic/launch/landing.md", "mimic/launch/handoff.md"],
     "why": "landing page, pricing, listing, launch plan, handoffs"},
    {"id": "deploy", "stage": "launch", "skill": "mimic-deploy",
     "files": ["mimic/deploy/preflight.md"],
     "why": "preflight gate, then live on your domain after your yes"},
]

VERDICT = re.compile(r"\b(go|no[- ]go|pivot|stop|narrow|pass(?:ed)?|fail(?:ed)?)\b", re.I)
SEVERITY = re.compile(r"\bS([1-4])\b")
CLOSED = re.compile(r"\b(fixed|closed|done|resolved|won'?t fix|wontfix|verified)\b", re.I)


TYPE_LINE = re.compile(r"^\s*[*_]*type[*_]*\s*:\s*(.+)$", re.I | re.M)


def business_type(project):
    """'app', 'offline' (service, local, physical) or None, from mimic/recon.md."""
    m = TYPE_LINE.search(read(os.path.join(project, "mimic", "recon.md")))
    if not m:
        return None
    value = m.group(1).lower()
    if "{{" in value:
        return None
    offline = re.search(r"\b(service|local|physical|shop|store|restaurant|food)\b", value)
    app = re.search(r"\b(app|website|web|saas|software)\b", value)
    if offline and not app:
        return "offline"
    return "app" if app else ("offline" if offline else None)


def exists(project, rel):
    path = os.path.join(project, rel)
    return os.path.isfile(path) and os.path.getsize(path) > 0


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def founder_home(home):
    """$FOUNDER_HOME if set, else <home>/.founder. Claude Code protects ~/.claude, so not there."""
    env = os.environ.get("FOUNDER_HOME")
    if env:
        return os.path.expanduser(env)
    return os.path.join(home, ".founder")


def founder_context(project, home):
    """Return (where, slug) of the business context in use, or (None, None)."""
    local = os.path.join(project, "founder", "context.md")
    if os.path.isfile(local):
        return local, None
    base = founder_home(home)
    slug = read(os.path.join(base, "active")).strip()
    if slug:
        path = os.path.join(base, "businesses", slug + ".md")
        if os.path.isfile(path):
            return path, slug
        return None, slug
    return None, None


def validate_verdict(project):
    """Read founder/validate.md for a result line. None if no result yet."""
    text = read(os.path.join(project, "founder", "validate.md"))
    if not text:
        return None
    for line in text.splitlines():
        low = line.lower()
        if re.match(r"^\s*[#*\-\s]*(verdict|decision|result|call)\b", low):
            m = VERDICT.search(line.split(":", 1)[-1] if ":" in line else line)
            if m:
                word = m.group(1).lower().replace(" ", "-")
                if word.startswith("pass"):
                    return "go"
                if word.startswith("fail"):
                    return "stop"
                return word
    return None


def matrix_summary(project):
    path = os.path.join(project, "mimic", "features.csv")
    if not os.path.isfile(path):
        return None
    must = done = 0
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                row = {(k or "").strip().lower(): (v or "").strip().lower()
                       for k, v in row.items()}
                if row.get("original", "yes") in ("no", "n", "false"):
                    continue
                if row.get("priority") in ("must", "p0") and row.get("clone") != "skip":
                    must += 1
                    if row.get("clone") in ("yes", "done"):
                        done += 1
    except (OSError, csv.Error):
        return None
    return {"must_total": must, "must_done": done}


def open_blockers(project):
    """Count open S1 and S2 rows in mimic/test/bugs.md. None if no bug log."""
    text = read(os.path.join(project, "mimic", "test", "bugs.md"))
    if not text:
        return None
    count = 0
    for line in text.splitlines():
        if not line.strip().startswith("|") or set(line.strip()) <= set("|-: "):
            continue
        m = SEVERITY.search(line)
        if m and m.group(1) in ("1", "2") and not CLOSED.search(line):
            count += 1
    return count


def find_skill(name, project, home, extra_dirs):
    """Return the folder a skill is installed in, or None."""
    places = [os.path.join(project, ".claude", "skills"),
              os.path.join(home, ".claude", "skills")] + list(extra_dirs)
    if name not in LINKED:
        places.insert(0, SKILLS_ROOT)  # synced and own skills ship in this repo
    for base in places:
        folder = os.path.join(base, name)
        if os.path.isfile(os.path.join(folder, "SKILL.md")):
            return folder
    return None


def get_linked_command():
    script = os.path.join(REPO_ROOT, "scripts", "get_linked.py")
    if os.path.isfile(script):
        return "python3 %s" % script
    return "python3 scripts/get_linked.py   (run it from the mimic-skills folder)"


def status(project, home=None, extra_dirs=()):
    project = os.path.abspath(project)
    home = home or os.path.expanduser("~")
    ctx_path, slug = founder_context(project, home)
    btype = business_type(project)
    steps = []
    for st in STEPS:
        have = [f for f in st["files"] if exists(project, f)]
        state = "done" if len(have) == len(st["files"]) else ("partial" if have else "todo")
        st = dict(st)
        if st.get("apps_only") and btype == "offline" and state == "todo":
            state = "skip"
        elif st.get("apps_only") and btype is None:
            st["optional"] = True  # type unknown: offer design, do not push it
        steps.append(dict(st, state=state, have=have,
                          missing=[f for f in st["files"] if f not in have]))
    linked = {n: find_skill(n, project, home, extra_dirs) for n in LINKED}
    synced = {n: find_skill(n, project, home, extra_dirs) for n in SYNCED}
    verdict = validate_verdict(project)
    matrix = matrix_summary(project)
    blockers = open_blockers(project)
    warnings = []
    if os.path.isdir(os.path.join(project, "replica")):
        warnings.append("A replica/ folder exists. The linked replica-* skills default to "
                        "replica/. Move those files into mimic/ so every skill sees them.")
    if ctx_path is None:
        warnings.append("No business context found (founder/context.md, or "
                        "~/.founder/active). Skills will ask for it once.")
    nxt, reason, gate = pick_next(steps, verdict, blockers, matrix)
    order = [s["skill"] for s in steps]
    cut = order.index(nxt) if nxt in order else len(order)
    optional_before = [{"skill": s["skill"], "why": s["why"]} for s in steps[:cut]
                       if s.get("optional") and s["state"] == "todo"
                       and not any(t["state"] != "todo" for t in steps[steps.index(s) + 1:]
                                   if not t.get("optional"))]
    result = {
        "project": project,
        "business_type": btype,
        "founder_context": ctx_path,
        "active_business": slug,
        "steps": [{k: s[k] for k in ("id", "stage", "skill", "state", "missing")}
                  for s in steps],
        "validate_verdict": verdict,
        "features": matrix,
        "open_s1_s2": blockers,
        "linked": {n: (p or None) for n, p in linked.items()},
        "synced": {n: (p or None) for n, p in synced.items()},
        "get_linked": get_linked_command(),
        "next": nxt,
        "next_reason": reason,
        "gate": gate,
        "optional_before": optional_before,
        "warnings": warnings,
    }
    if nxt in LINKED and not linked.get(nxt):
        result["next_blocked"] = ("%s is a linked skill by Jake Schincariol and is not "
                                  "installed. Install it with: %s" % (nxt, result["get_linked"]))
    elif nxt in SYNCED and not synced.get(nxt):
        result["next_blocked"] = ("%s is not installed here. It ships with Aya's "
                                  "other repos; install the plugin that has it, or "
                                  "skip this step if it is optional." % nxt)
    return result


def pick_next(steps, verdict, blockers, matrix):
    """Return (skill, reason, gate) for the next step."""
    by_id = {s["id"]: s for s in steps}
    gate = None
    if by_id["validate"]["state"] == "done" and verdict in ("stop", "no-go"):
        gate = ("The demand test said %s. Building now risks months on something "
                "people did not want. Rerun validate with a new angle, or decide on "
                "purpose to go ahead." % verdict)
    if blockers:
        gate = ("%d open S1 or S2 bug(s) in mimic/test/bugs.md. Deploy is blocked "
                "until they are fixed." % blockers)
    for s in steps:
        if s["state"] in ("done", "skip") or s.get("optional"):
            continue  # optional steps are offered, never pushed (see optional_before)
        if s["id"] == "validate" and by_id["reviews"]["state"] != "done":
            continue
        if s["id"] == "deploy" and blockers:
            return "mimic-test", "fix the open S1 and S2 bugs, then rerun the tests", gate
        return s["skill"], s["why"], gate
    if blockers:
        return "mimic-test", "fix the open S1 and S2 bugs", gate
    return None, "every step has its files. Next is launch day: see mimic/launch/handoff.md", gate


def render(r):
    out = ["Project: %s" % r["project"]]
    if r["founder_context"]:
        biz = (" (active business: %s)" % r["active_business"]) if r["active_business"] else ""
        out.append("Business context: %s%s" % (r["founder_context"], biz))
    else:
        out.append("Business context: not found")
    out.append("")
    stage = None
    for s in r["steps"]:
        if s["stage"] != stage:
            stage = s["stage"]
            out.append(stage)
        mark = {"done": "[x]", "partial": "[~]", "todo": "[ ]", "skip": "[-]"}[s["state"]]
        extra = ""
        if s["state"] == "skip":
            extra = "  skipped: no screens to design for this type of business"
        if s["state"] == "partial":
            extra = "  missing: " + ", ".join(s["missing"])
        out.append("  %s %-16s%s" % (mark, s["skill"], extra))
    out.append("")
    if r["validate_verdict"]:
        out.append("Demand test result: %s" % r["validate_verdict"])
    if r["features"]:
        f = r["features"]
        out.append("Must-have features built: %d of %d" % (f["must_done"], f["must_total"]))
    if r["open_s1_s2"] is not None:
        out.append("Open S1/S2 bugs: %d" % r["open_s1_s2"])
    out.append("")
    out.append("Linked skills (Jake Schincariol's replica-skill, MIT):")
    for n, p in r["linked"].items():
        out.append("  %-15s %s" % (n, "installed" if p else "NOT installed"))
    if not all(r["linked"].values()):
        out.append("  Get them with: %s" % r["get_linked"])
    missing_synced = [n for n, p in r["synced"].items() if not p]
    if missing_synced:
        out.append("Shared skills not found: %s" % ", ".join(missing_synced))
    for w in r["warnings"]:
        out.append("")
        out.append("Note: " + w)
    if r["gate"]:
        out.append("")
        out.append("GATE: " + r["gate"])
    out.append("")
    for o in r.get("optional_before", []):
        out.append("Optional first: /%s  (%s)" % (o["skill"], o["why"]))
    if r["next"]:
        out.append("Next: /%s  (%s)" % (r["next"], r["next_reason"]))
    else:
        out.append("Next: %s" % r["next_reason"])
    if r.get("next_blocked"):
        out.append("Blocked: " + r["next_blocked"])
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", default=".", help="the project folder (default: here)")
    ap.add_argument("--skills-dir", action="append", default=[],
                    help="another folder to look for installed skills in")
    ap.add_argument("--home", help=argparse.SUPPRESS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.project):
        print("status: %s is not a folder" % args.project, file=sys.stderr)
        return 2
    r = status(args.project, home=args.home, extra_dirs=args.skills_dir)
    print(json.dumps(r, indent=2) if args.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
