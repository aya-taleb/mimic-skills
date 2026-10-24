# Job spec: mimic-test

Written before reading any other version of this skill.

## The job

Prove the product works before real people use it. Turn the flows from recon into a test
plan, write end to end tests for the paths that matter, test the fixes that are the reason
this version exists, and keep an honest bug log with severity so deploy has a clear gate.

## Inputs

- `mimic/recon.md` (flows with edge cases), `mimic/features.csv`
- `mimic/fixes.md` (each fix needs a test that proves it)
- `mimic/architecture.md`, `mimic/backend.md`, the code

## Outputs

- `mimic/test/plan.md`: per flow, the happy path, edge cases, which test covers it, manual
  checks, and the result.
- End to end test files in the project (Playwright for web by default).
- `mimic/test/bugs.md`: one row per bug with id, title, severity S1 to S4, status, flow,
  steps to reproduce.

## What good looks like

- Every flow has a happy path test and its edge cases from recon.
- Every fix from reviews has a test named after it.
- Payments, auth, and email run in test mode.
- Severity has a fixed meaning. S1: data loss, money, security, or the core loop broken.
  S2: a must feature broken with no workaround. S3: has a workaround. S4: cosmetic.
- Results are real. Untested is marked untested. Nothing is marked passed without a run.
- Clear gate: no open S1 or S2 before deploy.
- Not an app: a dry run of the whole customer path (test order, test booking, test
  delivery) with a checklist, and the same bug log.

## Edge cases

- "Just mark it all passed": refuse. Offer the fastest real check instead.
- No code to run here: write the tests and the plan, mark results as not run, and say how
  to run them.

## Handoff

Next: replica-diff (linked) for parity, then replica-brand (linked), then mimic-launch.
