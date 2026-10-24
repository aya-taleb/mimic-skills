#!/usr/bin/env python3
"""Check a skills repo before a release or a pull request.

Checks:
  1. skills.json is valid and every skill it lists (except linked ones) has a folder.
  2. Every skill folder has a SKILL.md with frontmatter: name matches the folder,
     description present and under 1024 characters.
  3. Every skill that is not synced or linked has at least one test case under evals/
     with prompt.md, case.yaml and at least one grader.
  4. Writing rules in Markdown files: no em dashes and none of the banned words.
     Text inside code fences, CREDITS.md, and lines marked <!-- allow-words --> are skipped.

Exit code 0 when clean, 1 when anything fails. Standard library only.
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

BANNED = [
    "delve", "leverage", "seamless", "seamlessly", "streamline", "comprehensive",
    "journey", "unlock", "elevate", "empower", "foster", "thoughtful", "relatable",
    "humor", "storytelling", "simple", "robust", "crucial", "utilize", "synergy",
    "cutting-edge", "game-changer", "revolutionize", "tapestry", "testament",
    "moreover", "furthermore", "in today's fast-paced world", "let's dive in",
]
EM_DASH = "—"
SKIP_FILES = {"CREDITS.md", "LICENSE", "LICENSE.md"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", "results"}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    data = {}
    key = None
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            data[key] = "" if val in (">-", ">", "|", "|-") else val
        elif key and line.startswith((" ", "\t")):
            data[key] = (data[key] + " " + line.strip()).strip()
    return data


def banned_hits(line):
    low = line.lower()
    hits = []
    for word in BANNED:
        pattern = r"(?<![a-z])" + re.escape(word) + r"(?![a-z])"
        if re.search(pattern, low):
            hits.append(word)
    return hits


def check_writing(errors):
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".md") or name in SKIP_FILES:
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, ROOT)
            in_fence = False
            for n, line in enumerate(read(path).splitlines(), 1):
                if line.strip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence or "allow-words" in line:
                    continue
                if EM_DASH in line:
                    errors.append("%s:%d em dash" % (rel, n))
                for word in banned_hits(line):
                    errors.append("%s:%d banned word '%s'" % (rel, n, word))


def check_skills(errors):
    manifest_path = os.path.join(ROOT, "skills.json")
    if not os.path.exists(manifest_path):
        errors.append("skills.json is missing")
        return
    try:
        manifest = json.loads(read(manifest_path))
    except ValueError as exc:
        errors.append("skills.json is not valid JSON: %s" % exc)
        return
    listed = {}
    for entry in manifest.get("skills", []):
        if "name" not in entry or "status" not in entry:
            errors.append("skills.json entry missing name or status: %r" % entry)
            continue
        listed[entry["name"]] = entry
    skills_dir = os.path.join(ROOT, "skills")
    present = set(os.listdir(skills_dir)) if os.path.isdir(skills_dir) else set()
    for name, entry in listed.items():
        status = entry["status"]
        if status == "linked":
            for key in ("repo", "commit", "path"):
                if not entry.get(key):
                    errors.append("linked skill %s needs '%s' in skills.json" % (name, key))
            continue
        if name not in present:
            if status == "synced":
                continue  # copied in by the sync step
            errors.append("skill %s is in skills.json but has no folder" % name)
    for name in sorted(present):
        folder = os.path.join(skills_dir, name)
        if not os.path.isdir(folder):
            continue
        if name not in listed:
            errors.append("skills/%s is not listed in skills.json" % name)
        skill_md = os.path.join(folder, "SKILL.md")
        if not os.path.exists(skill_md):
            errors.append("skills/%s has no SKILL.md" % name)
            continue
        fm = frontmatter(read(skill_md))
        if fm is None:
            errors.append("skills/%s/SKILL.md has no frontmatter" % name)
            continue
        if fm.get("name") != name:
            errors.append("skills/%s: frontmatter name is %r" % (name, fm.get("name")))
        desc = fm.get("description", "")
        if not desc:
            errors.append("skills/%s: description is empty" % name)
        elif len(desc) > 1024:
            errors.append("skills/%s: description is %d characters (max 1024)" % (name, len(desc)))
        status = listed.get(name, {}).get("status", "")
        if status in ("synced", "linked"):
            continue
        evals = os.path.join(folder, "evals")
        cases = []
        if os.path.isdir(evals):
            for case in os.listdir(evals):
                cdir = os.path.join(evals, case)
                if not os.path.isdir(cdir) or case in ("files", "results"):
                    continue
                ok = (
                    os.path.exists(os.path.join(cdir, "prompt.md"))
                    and os.path.exists(os.path.join(cdir, "case.yaml"))
                    and os.path.isdir(os.path.join(cdir, "graders"))
                    and os.listdir(os.path.join(cdir, "graders"))
                )
                if ok:
                    cases.append(case)
                else:
                    errors.append("skills/%s/evals/%s is incomplete" % (name, case))
        if not cases:
            errors.append("skills/%s has no test cases in evals/" % name)


def main():
    errors = []
    check_skills(errors)
    check_writing(errors)
    if errors:
        print("validate: %d problem(s)" % len(errors))
        for err in errors:
            print("  - " + err)
        return 1
    print("validate: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
