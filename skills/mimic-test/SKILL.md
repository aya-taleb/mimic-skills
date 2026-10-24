---
name: mimic-test
description: >-
  Proves your version works before real people use it: a test plan from the recon flows
  and their edge cases, end to end tests for the paths that matter (Playwright for web by
  default), a named test for every review fix, payments and email in test mode, and an
  honest bug log with fixed severities that gates deploy. For services and local
  businesses, a dry run of the whole customer path. Use when the user says "test it",
  "write tests", "e2e tests", "QA", "find bugs", "is it ready", "test plan", "do a dry
  run", "log this bug", or after /mimic-backend. Never marks anything passed without a run.
---

# mimic-test

Testing here has one job: find what would hurt a real customer before one finds it. A
green report that nobody ran is worse than no report, because it tells the user to stop
looking.

## Reads and writes

Reads: `mimic/recon.md` (flows F01... with edge cases), `mimic/features.csv`,
`mimic/fixes.md` (every fix needs a test), `mimic/architecture.md`, `mimic/backend.md`
(services in test mode, the security checklist), and the code.

Writes:

- `mimic/test/plan.md` (template: `references/plan-template.md`)
- end to end test files in the project (for web, `tests/e2e/*.spec.ts` with Playwright)
- `mimic/test/bugs.md`, the bug log (format below)

Tool:

```bash
python3 scripts/bugs.py mimic/test/bugs.md          # counts and problems
python3 scripts/bugs.py mimic/test/bugs.md --gate   # exit 1 if any S1 or S2 is open
```

## Severity has one meaning

Fixed definitions stop "it's only an S3" arguments the night before launch.

| severity | means | example |
| --- | --- | --- |
| S1 | data loss, money, security, or the core loop broken | double booking goes through; user sees another user's orders |
| S2 | a must feature broken, no workaround | reschedule link errors |
| S3 | broken, but there is a workaround | filter resets after refresh |
| S4 | cosmetic | button misaligned on one phone |

Deploy is blocked while any S1 or S2 is `open`, `fixing` or `fixed` but not yet
`verified` by a rerun. An S1 cannot be `wontfix`.

## Step 1: the plan

Always write `plan.md`, even when the job is only logging bugs: it is what the gate and
the next skills read. For each flow in `recon.md`, one block in `plan.md`, including flows
not built yet (mark them "not built yet" but still write the happy path and edge cases,
so the tests are ready when the code is):

- the happy path, step by step, with what the user should see at the end
- every edge case recon listed, plus the ones every product has: empty data, slow network,
  double submit, back button, expired session, a second tab, small screen, keyboard only
- which automated test covers it, or "manual" with the steps
- the result: `pass`, `fail` (with bug id), or `not run`

Then a block per fix in `fixes.md`, named after the fix ("fix 3: time zone confirm step"),
with the check that proves it works. The fixes are why this product exists, so they get
tested like the core loop.

Add the money and trust checks: checkout in test mode with the provider's test cards,
webhook replay handled once, cancel works, emails arrive with working links, user A
cannot see user B's data.

## Step 2: write the tests

For web apps, Playwright end to end tests by default, one spec per flow. If the project
already uses another tool (Cypress, Detox for mobile), use that. Keep tests readable:
one test per behavior, named in plain words, using roles and labels to find elements
rather than CSS classes, so they survive the rebrand.

```ts
test("a taken slot cannot be booked twice", async ({ page }) => { ... });
```

Seed test data through the app's own API or a seed script, never against production.

Only list a test file in the plan if you wrote it. A flow whose spec you did not write is
"manual" or "spec to write", not a file name. Element names you guessed (labels, routes)
are marked as guesses in a comment at the top of the spec.

## Step 3: run them, or say they did not run

Run the suite if the environment allows (`npx playwright test`). Paste the summary line.
A bug you found by reading code, not by running it, is still logged, with "found by
reading the code, not reproduced" in its steps. Its plan result is `not run`, not `fail`.
If you cannot run it here, mark every result `not run`, give the exact commands, and say
what passing looks like. Never write `pass` for a test that did not run. If the user asks
you to "just mark it all passed", decline and offer the fastest real check instead.

## Step 4: the bug log

Every failure becomes a row in `mimic/test/bugs.md`:

```
| id | title | severity | status | flow | found | steps |
| --- | --- | --- | --- | --- | --- | --- |
| B001 | Second booking for a taken slot goes through | S1 | open | F01 | 2026-10-20 | 1. Open /book/demo in two tabs 2. Pick 10:00 in both 3. Submit both |
```

Title says what is wrong, not what to do. Steps let someone else see it happen. Then:

```bash
python3 scripts/bugs.py mimic/test/bugs.md
```

It checks each row is complete and the severities and statuses are valid, and prints
whether deploy is blocked. Fix the log until it has no problems. Always run it before you
reply, and quote its last line.

Count the summary table from the rows you wrote (planned, passed, failed, not run), so
the numbers add up. When asked to skip testing, the fast real check you offer is a smoke
test: the core loop once, by hand or with one spec, in under 15 minutes.

When a bug is fixed, rerun its test, then mark it `verified`. Fixed but not rerun is still
open, because that is how the same bug ships twice.

## Services, local businesses and physical products

The test is a dry run of the customer path in `recon.md`: place a real test order or
booking, follow each step's checklist, receive every message, take a payment in test
mode, and try the edge cases (sold out, late, wrong item, refund, cancel). One person
plays the customer, one runs the business side. Log what breaks in the same bug log with
the same severities. A late lunch for a whole office is an S1, and so is food that breaks
a dietary rule. Copy each problem into the log in the notes' own facts; do not add times
or details the notes do not have.

## Writing

Every file and reply is read by a busy founder. Plain words, sentences under 25 words, no
em dashes, no hype. Skip these words in everything you write:
delve, leverage, seamless, streamline, comprehensive, journey, unlock, elevate, empower, foster, robust, crucial, utilize, simple. <!-- allow-words -->
If the humanize skill is installed, run copy that a person will publish or send through it.

## Output

`plan.md`, the test files, `bugs.md`, the result of `bugs.py`, and a summary: tests run
and passed, tests not run and why, open bugs by severity, and whether the gate passes.
Always end the reply with the next step from the line below, by skill name.

Next: fix open S1 and S2 bugs and rerun. When the gate passes: `/replica-diff` for the
parity score, then `/replica-brand` (both are linked skills by Jake Schincariol; if they
are not installed, run `python3 scripts/get_linked.py` from the mimic-skills folder), then
`/mimic-launch`.
