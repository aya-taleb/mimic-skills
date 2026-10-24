# The mimic chain

Each step, what it writes, and where the skill comes from. A step counts as done when its
files exist and are not empty.

| # | stage | skill | writes | comes from |
| --- | --- | --- | --- | --- |
| 1 | research | market-research (optional) | founder/market.md | entrepreneur-skills (synced) |
| 2 | research | competitors (optional) | founder/competitors.md | biz-launch-skills (synced) |
| 3 | research | mimic-recon | mimic/recon.md, mimic/features.csv | this repo |
| 4 | reviews | mimic-reviews | mimic/reviews.csv, mimic/feedback.md, mimic/fixes.md, mimic/pain-points.csv | this repo |
| 5 | validate | validate | founder/validate.md | entrepreneur-skills (synced) |
| 6 | build | mimic-architect | mimic/architecture.md | this repo |
| 7 | build | replica-design (apps only) | mimic/design/tokens.json, components.md | Jake's replica-skill (linked) |
| 8 | build | mimic-build | code, mimic/build-log.md | this repo |
| 9 | build | mimic-backend | mimic/backend.md, .env.example | this repo |
| 10 | build | mimic-test | mimic/test/plan.md, mimic/test/bugs.md | this repo |
| 11 | build | replica-diff | mimic/parity.md | Jake's replica-skill (linked) |
| 12 | build | replica-brand | mimic/brand.md, mimic/brand.json | Jake's replica-skill (linked) |
| 13 | launch | mimic-launch | mimic/launch/landing.md, pricing.md, plan.md, handoff.md | this repo |
| 14 | launch | mimic-deploy | mimic/deploy/preflight.md, runbook.md | this repo |
| - | launch | launch-video (optional) | media/ | multimedia-skills (synced) |

After step 14 the work moves to other repos, named in `mimic/launch/handoff.md`:
biz-boost-skills (lead-gen reads `mimic/pain-points.csv`, lead-email, local-outreach),
linkedin-boost-skills and instagram-boost-skills.

## Linked skills

Jake Schincariol's replica-skill, MIT, pinned at commit
77c9436fb3d18c3d58169efb8caf4fe906b0dc51. Install with `python3 scripts/get_linked.py`
from the mimic-skills folder. Add `--project` to install into `./.claude/skills/`
instead of `~/.claude/skills/`.

They were written for a `replica/` folder. Same file names, different folder: tell them
to use `mimic/`.

| linked skill | used for | its tool |
| --- | --- | --- |
| replica-design | tokens and component specs | contrast.py tokens.json |
| replica-diff | parity score and layout diff | parity.py features.csv, imgdiff.py |
| replica-brand | name, palette, voice, leftover sweep | sweep.py . --config mimic/brand.json |

## Checking by hand

No Python? Look for each file in the table. For the demand test, open
`founder/validate.md` and find the line that starts with "Verdict" or "Decision". For
bugs, count rows in `mimic/test/bugs.md` with S1 or S2 that are not fixed or closed.
