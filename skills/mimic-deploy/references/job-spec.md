# Job spec: mimic-deploy

Written before reading any other version of this skill.

## The job

Put it live on the user's own domain, safely, and only after the user says yes. First a
preflight gate that blocks launch when something is wrong. Then production setup, domain
records, monitoring, and a way back if it breaks.

## Inputs

- `mimic/test/bugs.md` (open S1 or S2 blocks)
- `mimic/features.csv` and the linked parity tool (must features missing blocks)
- `mimic/brand.json` and the linked rebrand sweep (anything of the original left blocks)
- `mimic/launch/` (listing and copy checks, proof check)
- `mimic/architecture.md`, `mimic/backend.md` (services, env vars)

## Outputs

- `mimic/deploy/preflight.md`: each check, pass, fail or skipped with reason, and the verdict.
- `mimic/deploy/runbook.md`: hosting, env vars to set, migrations, domain DNS records,
  monitoring, backups, rollback, launch day steps, who to call.

## What good looks like

- Preflight runs real checks and shows the output. Blocks on: open S1 or S2, missing must
  features, a dirty rebrand sweep, secrets in the repo, payments still in test mode at
  launch, missing privacy policy and terms.
- Nothing goes live without the user's explicit yes after they see the preflight.
- DNS records are given as records to add at the registrar, with what each does.
- Monitoring: errors, uptime, and basic analytics, with alerts going somewhere the user sees.
- A rollback that was tried at least once on staging.
- Not an app: go-live checklist for the site, booking, payments in live mode, Google
  Business Profile, permits from ops, and a soft opening.

## Edge cases

- "Skip the checks and push it": refuse to skip the sweep and the bug gate. Offer a preview
  deploy that is not public.
- Linked tools not installed: say how to get them (`python3 scripts/get_linked.py`), mark
  those checks as not run, and do not call the gate passed.

## Handoff

After go-live: the launch day part of `mimic/launch/plan.md`, then biz-boost and the
social plans named in `mimic/launch/handoff.md`.
