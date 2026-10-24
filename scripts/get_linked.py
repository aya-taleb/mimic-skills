#!/usr/bin/env python3
"""Install the linked skills this repo uses from their original authors.

Some skills in this repo call tools written by other people. We don't copy those here.
This script fetches each one from its author's repo at a fixed commit (so it can't change
under you) and copies only the skill folders this repo needs.

Usage:
  python3 scripts/get_linked.py              # install into ~/.claude/skills/
  python3 scripts/get_linked.py --project    # install into ./.claude/skills/
  python3 scripts/get_linked.py --list       # show what would be installed

Standard library only. Needs git.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def linked_skills():
    with open(os.path.join(ROOT, "skills.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    return [s for s in manifest.get("skills", []) if s.get("status") == "linked"]


def fetch(repo, commit, workdir):
    url = "https://github.com/%s.git" % repo
    subprocess.run(["git", "init", "-q", workdir], check=True)
    subprocess.run(["git", "-C", workdir, "remote", "add", "origin", url], check=True)
    subprocess.run(["git", "-C", workdir, "fetch", "-q", "--depth", "1", "origin", commit], check=True)
    subprocess.run(["git", "-C", workdir, "checkout", "-q", "FETCH_HEAD"], check=True)


def main():
    parser = argparse.ArgumentParser(description="Install linked skills.")
    parser.add_argument("--project", action="store_true", help="install into ./.claude/skills")
    parser.add_argument("--dest", help="install into this folder instead")
    parser.add_argument("--list", action="store_true", help="only list them")
    args = parser.parse_args()

    skills = linked_skills()
    if not skills:
        print("This repo has no linked skills.")
        return 0
    if args.list:
        for s in skills:
            print("%-16s from %s @ %s (%s)" % (s["name"], s["repo"], s["commit"][:7], s.get("license", "see repo")))
        return 0

    if args.dest:
        dest = os.path.expanduser(args.dest)
    elif args.project:
        dest = os.path.join(os.getcwd(), ".claude", "skills")
    else:
        dest = os.path.expanduser("~/.claude/skills")
    os.makedirs(dest, exist_ok=True)

    by_repo = {}
    for s in skills:
        by_repo.setdefault((s["repo"], s["commit"]), []).append(s)

    for (repo, commit), items in by_repo.items():
        with tempfile.TemporaryDirectory() as tmp:
            print("Fetching %s @ %s" % (repo, commit[:7]))
            try:
                fetch(repo, commit, tmp)
            except subprocess.CalledProcessError:
                print("  could not fetch %s. Check your connection, or that the repo still exists." % repo)
                continue
            for s in items:
                src = os.path.join(tmp, s["path"])
                if not os.path.isdir(src):
                    print("  %s not found at %s in that commit" % (s["name"], s["path"]))
                    continue
                target = os.path.join(dest, s["name"])
                if os.path.exists(target):
                    print("  %s already installed, skipping (delete it to reinstall)" % s["name"])
                    continue
                shutil.copytree(src, target, ignore=shutil.ignore_patterns(".git"))
                lic = os.path.join(tmp, "LICENSE")
                if os.path.exists(lic):
                    shutil.copy(lic, os.path.join(target, "LICENSE-upstream"))
                print("  installed %s -> %s" % (s["name"], target))
    print("Done. These skills belong to their authors; see each LICENSE-upstream file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
