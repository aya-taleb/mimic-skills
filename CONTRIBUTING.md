# Contributing

Thanks for helping. Fixes, better examples and new test cases are all welcome.

## Where to send a fix

Some skills here are shared across several of my repos. Each one has a single home.
Fix it in its home repo, and the change gets copied everywhere else.

| skill | home repo |
| --- | --- |
| market-research | [entrepreneur-skills](https://github.com/aya-taleb/entrepreneur-skills) |
| validate | [entrepreneur-skills](https://github.com/aya-taleb/entrepreneur-skills) |
| competitors | [biz-launch-skills](https://github.com/aya-taleb/biz-launch-skills) |
| launch-video | [multimedia-skills](https://github.com/aya-taleb/multimedia-skills) |
| replica-design, replica-diff, replica-brand | not copied here. They are Jake Schincariol's: send fixes to [replica-skill](https://github.com/Jakeschincariol/replica-skill) |
| every mimic-* skill | this repo |

If you edit a copy here instead of the home, the pull request check will fail and point
you to the right repo. That's on purpose, so your fix doesn't get wiped on the next sync.

## How to make a change

1. Fork the repo and make your change on a branch.
2. If you changed a Python tool, run its tests:
   `python3 -m unittest discover -s tests -v`
3. Run the checks: `python3 scripts/validate.py`
4. If you changed how a skill behaves, add or update a test case in
   `skills/<skill>/evals/`. Each case is a folder with a prompt and a few checkable
   statements. Copy an existing case to start.
5. Open a pull request. Say what you changed and why, in a few lines.

## House rules for writing

- Plain words, short sentences. Write like a person.
- No em dashes.
- Skip the stock AI words listed in `scripts/validate.py`. The check will flag them.
- Never make up facts, numbers, quotes or sources in a skill or an example.

## Good first issues

Look for the `good first issue` label. Adding words to the review themes (skills/mimic-reviews/scripts/themes*.json), a new test
case, or a clearer example are all great places to start.
