#!/usr/bin/env python3
"""Fail a pull request that edits a synced copy of a skill.

Synced skills have one home repo. Edits must happen there, or the next sync wipes them.
This script lists files changed against a base branch and fails if any sit inside a
skill whose status in skills.json is "synced".

Usage: python3 scripts/check_synced.py --base origin/main
Standard library only. Needs git.
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def changed_files(base):
    out = subprocess.run(
        ["git", "diff", "--name-only", base + "...HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/main")
    args = parser.parse_args()
    with open(os.path.join(ROOT, "skills.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    synced = {s["name"]: s.get("home", "its home repo")
              for s in manifest.get("skills", []) if s.get("status") == "synced"}
    problems = []
    for path in changed_files(args.base):
        parts = path.split("/")
        if len(parts) > 2 and parts[0] == "skills" and parts[1] in synced:
            problems.append((path, synced[parts[1]]))
    if problems:
        print("These files belong to skills whose home is another repo:")
        for path, home in problems:
            print("  - %s  (edit it in github.com/aya-taleb/%s)" % (path, home))
        print("Please move your change to the home repo. Thanks!")
        return 1
    print("check_synced: no synced copies edited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
